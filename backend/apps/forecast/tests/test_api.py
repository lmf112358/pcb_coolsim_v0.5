"""负荷预测 API 测试（F10-001~021）"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="fcuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestForecastScenarioAPI:
    """F10-001~004 场景 CRUD"""

    def test_create_scenario(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/projects/{project.id}/forecast-scenarios/", {
            "name": "7月预测", "start_date": "2024-07-01",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["status"] == "active"

    def test_list_scenarios(self, db, project, engineer_role):
        from apps.forecast.models import ForecastScenario
        ForecastScenario.objects.create(project=project, name="场景1", start_date="2024-07-01")
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/projects/{project.id}/forecast-scenarios/")
        assert resp.status_code == 200
        assert len(resp.data["results"]) >= 1

    def test_update_status(self, db, project, engineer_role):
        """F10-003/004: 状态切换 active/paused/archived"""
        from apps.forecast.models import ForecastScenario
        sc = ForecastScenario.objects.create(project=project, name="s", start_date="2024-07-01")
        c = auth_client(db, engineer_role)
        resp = c.patch(f"/api/v1/forecast-scenarios/{sc.id}/status/", {
            "status": "paused",
        }, format="json")
        assert resp.status_code == 200
        assert resp.data["status"] == "paused"

    def test_delete_scenario(self, db, project, engineer_role):
        from apps.forecast.models import ForecastScenario
        sc = ForecastScenario.objects.create(project=project, name="del", start_date="2024-07-01")
        c = auth_client(db, engineer_role)
        resp = c.delete(f"/api/v1/forecast-scenarios/{sc.id}/")
        assert resp.status_code == 204


class TestForecastRunAPI:
    """F10-014~018 运行预测"""

    def test_run_forecast(self, db, project, room_standard, engineer_role):
        from apps.forecast.models import ForecastScenario
        from apps.forecast.services import seed_default_coefficients
        from apps.calculation.models import RoomCalcResult
        seed_default_coefficients()
        RoomCalcResult.objects.create(room=room_standard, terminal_load=Decimal("10"))
        sc = ForecastScenario.objects.create(project=project, name="运行", start_date="2024-07-01")
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/forecast-scenarios/{sc.id}/run/", {
            "room_id": room_standard.id,
            "weather_temps": ["30", "35"],
            "rates": ["100", "100"],
        }, format="json")
        assert resp.status_code == 200
        assert "results" in resp.data
        assert len(resp.data["results"]) == 2

    def test_get_results(self, db, project, room_standard, engineer_role):
        from apps.forecast.models import ForecastScenario, ForecastHourlyResult
        from apps.forecast.services import seed_default_coefficients
        from apps.calculation.models import RoomCalcResult
        seed_default_coefficients()
        RoomCalcResult.objects.create(room=room_standard, terminal_load=Decimal("10"))
        sc = ForecastScenario.objects.create(project=project, name="结果", start_date="2024-07-01")
        c = auth_client(db, engineer_role)
        c.post(f"/api/v1/forecast-scenarios/{sc.id}/run/", {
            "room_id": room_standard.id,
            "weather_temps": ["30"], "rates": ["100"],
        }, format="json")
        resp = c.get(f"/api/v1/forecast-scenarios/{sc.id}/results/")
        assert resp.status_code == 200
