"""静态计算 API 测试（F4-001，触发计算并落库）"""
import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from apps.projects.models import Room
from apps.calculation.models import RoomCalcResult


def make_auth_client(db, engineer_role):
    """已认证的 APIClient（force_authenticate 走 DRF 认证）"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        username="apiuser", password="Test@12345", role=engineer_role,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestStaticCalcAPI:
    """F4-001: 触发静态冷量计算"""

    def test_calc_single_room(self, db, room_standard, engineer_role):
        """POST 触发单房间计算，落库 RoomCalcResult"""
        client = make_auth_client(db, engineer_role)
        resp = client.post(f"/api/v1/calc/static/{room_standard.id}/", format="json")
        assert resp.status_code == 201, resp.data
        assert RoomCalcResult.objects.filter(room=room_standard).exists()
        result = RoomCalcResult.objects.get(room=room_standard)
        assert result.terminal_load > 0
        assert result.fresh_air_volume > 0

    def test_calc_result_fields_complete(self, db, room_standard, engineer_role):
        """计算结果含全部中间值"""
        client = make_auth_client(db, engineer_role)
        client.post(f"/api/v1/calc/static/{room_standard.id}/", format="json")
        result = RoomCalcResult.objects.get(room=room_standard)
        assert result.civil_load is not None
        assert result.lighting_load is not None
        assert result.terminal_load is not None
        assert result.outdoor_enthalpy_calc is not None
        assert result.indoor_enthalpy_calc is not None

    def test_calc_idempotent(self, db, room_standard, engineer_role):
        """重复计算更新而非新增（OneToOne）"""
        client = make_auth_client(db, engineer_role)
        client.post(f"/api/v1/calc/static/{room_standard.id}/", format="json")
        client.post(f"/api/v1/calc/static/{room_standard.id}/", format="json")
        assert RoomCalcResult.objects.filter(room=room_standard).count() == 1

    def test_calc_room_not_found(self, db, engineer_role):
        """不存在的 room_id 返回 404"""
        client = make_auth_client(db, engineer_role)
        resp = client.post("/api/v1/calc/static/99999/", format="json")
        assert resp.status_code == 404

    def test_calc_requires_auth(self, db, room_standard):
        """未认证请求被拒"""
        client = APIClient()
        resp = client.post(f"/api/v1/calc/static/{room_standard.id}/", format="json")
        assert resp.status_code == 401
