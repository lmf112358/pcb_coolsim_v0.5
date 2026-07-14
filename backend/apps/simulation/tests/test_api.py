"""动态仿真 API 测试（F6-020~023，F7-027~029）"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.calculation.models import RoomCalcResult
from apps.simulation.models import SimulationRun
from apps.simulation.services import simulate_weather_driven


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="simuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def room_with_calc(room_standard):
    """已静态计算的 room"""
    RoomCalcResult.objects.update_or_create(
        room=room_standard,
        defaults={
            "terminal_load": Decimal("20"), "fresh_air_volume": Decimal("500"),
            "indoor_enthalpy_calc": Decimal("55.65"),
            "civil_load": Decimal("3"), "lighting_load": Decimal("1.5"),
        },
    )
    return room_standard


class TestSimulateTriggerAPI:
    """F6-020~023: 触发动态仿真"""

    def test_trigger_simulation(self, db, room_with_calc, engineer_role):
        """POST /simulations/ 触发仿真，返回批次"""
        c = auth_client(db, engineer_role)
        # 构造简化气象
        import numpy as np
        weather = {
            "temp_dry": [30.0] * 24,
            "temp_wet": [27.0] * 24,
            "pressure": [1004.0] * 24,
        }
        resp = c.post("/api/v1/simulations/", {
            "room_id": room_with_calc.id,
            "weather": weather,
        }, format="json")
        assert resp.status_code == 201, resp.data
        assert "batch_id" in resp.data
        assert SimulationRun.objects.filter(room=room_with_calc).exists()

    def test_trigger_requires_auth(self, db, room_with_calc):
        """未认证 401"""
        c = APIClient()
        resp = c.post("/api/v1/simulations/", {"room_id": room_with_calc.id}, format="json")
        assert resp.status_code == 401

    def test_trigger_room_not_found(self, db, engineer_role):
        """不存在 room 404"""
        c = auth_client(db, engineer_role)
        resp = c.post("/api/v1/simulations/", {"room_id": 99999, "weather": {}}, format="json")
        assert resp.status_code == 404

    def test_trigger_no_static_calc(self, db, room_standard, engineer_role):
        """无静态计算结果报错（桥梁缺失）"""
        c = auth_client(db, engineer_role)
        resp = c.post("/api/v1/simulations/", {
            "room_id": room_standard.id,
            "weather": {"temp_dry": [30], "temp_wet": [27], "pressure": [1004]},
        }, format="json")
        assert resp.status_code == 400

    def test_simulation_results_extremes(self, db, room_with_calc, engineer_role):
        """仿真结果含极值统计"""
        c = auth_client(db, engineer_role)
        resp = c.post("/api/v1/simulations/", {
            "room_id": room_with_calc.id,
            "weather": {"temp_dry": [30.0] * 24, "temp_wet": [27.0] * 24, "pressure": [1004.0] * 24},
        }, format="json")
        assert resp.status_code == 201
        assert "extremes" in resp.data
        assert "max_load" in resp.data["extremes"]

    def test_get_simulation_result(self, db, room_with_calc, engineer_role):
        """GET /simulations/{batch_id}/ 获取结果"""
        c = auth_client(db, engineer_role)
        trigger = c.post("/api/v1/simulations/", {
            "room_id": room_with_calc.id,
            "weather": {"temp_dry": [30.0] * 12, "temp_wet": [27.0] * 12, "pressure": [1004.0] * 12},
        }, format="json")
        batch_id = trigger.data["batch_id"]
        resp = c.get(f"/api/v1/simulations/{batch_id}/")
        assert resp.status_code == 200
        assert "result_summary" in resp.data
        assert "extremes" in resp.data["result_summary"]
