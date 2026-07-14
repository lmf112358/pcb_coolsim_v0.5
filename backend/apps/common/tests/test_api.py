"""common 系统设置 API 测试（F9-001~018）"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="cuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestCityConfigAPI:
    """F4-038~042 / F9-011~013: 国标参数查询"""

    def test_list_cities(self, db, city_guangzhou, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get("/api/v1/cities/")
        assert resp.status_code == 200
        assert len(resp.data["results"]) >= 1

    def test_city_detail(self, db, city_guangzhou, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/cities/{city_guangzhou.id}/")
        assert resp.status_code == 200
        assert resp.data["city_name"] == "广州"
        assert resp.data["temp_dry_ac_summer"] == "34.2"

    def test_search_by_name(self, db, city_guangzhou, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get("/api/v1/cities/?search=广州")
        assert resp.status_code == 200
        assert any(r["city_name"] == "广州" for r in resp.data["results"])


class TestWaterTempConfigAPI:
    """F9-001~005: 冷冻水温度配置 CRUD"""

    def test_create_config(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/projects/{project.id}/water-temp-configs/", {
            "temp_type_name": "低温冷冻水",
            "supply_temp": "7", "return_temp": "12",
        }, format="json")
        assert resp.status_code == 201

    def test_list_configs(self, db, project, engineer_role):
        from apps.common.models import WaterTempConfig
        WaterTempConfig.objects.create(
            project=project, temp_type_name="中温", supply_temp=12, return_temp=17
        )
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/projects/{project.id}/water-temp-configs/")
        assert resp.status_code == 200
        assert len(resp.data["results"]) >= 1

    def test_update_config(self, db, project, engineer_role):
        from apps.common.models import WaterTempConfig
        wtc = WaterTempConfig.objects.create(
            project=project, temp_type_name="低温", supply_temp=7, return_temp=12
        )
        c = auth_client(db, engineer_role)
        resp = c.patch(f"/api/v1/water-temp-configs/{wtc.id}/", {
            "return_temp": "13",
        }, format="json")
        assert resp.status_code == 200
        wtc.refresh_from_db()
        assert wtc.return_temp == Decimal("13")

    def test_delete_config(self, db, project, engineer_role):
        from apps.common.models import WaterTempConfig
        wtc = WaterTempConfig.objects.create(
            project=project, temp_type_name="待删", supply_temp=7, return_temp=12
        )
        c = auth_client(db, engineer_role)
        resp = c.delete(f"/api/v1/water-temp-configs/{wtc.id}/")
        assert resp.status_code == 204


class TestDefaultConfigAPI:
    """F9-006~010: 默认值配置"""

    def test_get_defaults(self, db, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get("/api/v1/defaults/")
        assert resp.status_code == 200
