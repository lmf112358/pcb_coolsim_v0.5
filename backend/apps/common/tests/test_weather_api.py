"""气象数据 API 测试（F4-043~050）"""
from decimal import Decimal
from datetime import datetime, timedelta

import pytest
from rest_framework.test import APIClient

from apps.common.models import WeatherRecord


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="wuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def create_weather_records(city, count=48):
    """创建 count 条气象记录"""
    base = datetime(2024, 7, 1)
    records = []
    for i in range(count):
        records.append(WeatherRecord(
            city=city, timestamp=base + timedelta(hours=i),
            dry_bulb_temp=Decimal(str(25 + i * 0.1)),
            wet_bulb_temp=Decimal(str(20 + i * 0.1)),
            humidity=Decimal("60"),
            atmospheric_pressure=Decimal("1004"),
        ))
    WeatherRecord.objects.bulk_create(records)
    return records


class TestWeatherSummaryAPI:
    """F4-048: 气象数据概览"""

    def test_summary(self, db, city_guangzhou, engineer_role):
        create_weather_records(city_guangzhou, 48)
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/weather/{city_guangzhou.id}/summary/")
        assert resp.status_code == 200
        assert resp.data["record_count"] == 48
        assert "time_range_start" in resp.data
        assert "temp_range" in resp.data

    def test_summary_empty_city(self, db, city_guangzhou, engineer_role):
        """无数据的城市"""
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/weather/{city_guangzhou.id}/summary/")
        assert resp.status_code == 200
        assert resp.data["record_count"] == 0


class TestWeatherUploadAPI:
    """F4-050: 手动上传气象数据（CSV）"""

    def test_upload_csv(self, db, city_guangzhou, engineer_role):
        """上传 CSV 气象数据"""
        c = auth_client(db, engineer_role)
        csv_content = "timestamp,dry_bulb_temp,wet_bulb_temp,humidity\n"
        csv_content += "2024-07-01T00:00:00,30.0,27.0,65\n"
        csv_content += "2024-07-01T01:00:00,31.0,28.0,64\n"
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("weather.csv", csv_content.encode("utf-8"), content_type="text/csv")
        resp = c.post(f"/api/v1/weather/{city_guangzhou.id}/upload/",
                      {"file": f}, format="multipart")
        assert resp.status_code == 201
        assert WeatherRecord.objects.filter(city=city_guangzhou).count() == 2

    def test_upload_invalid_csv(self, db, city_guangzhou, engineer_role):
        """非法 CSV 返回 400"""
        c = auth_client(db, engineer_role)
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("bad.csv", b"garbage", content_type="text/csv")
        resp = c.post(f"/api/v1/weather/{city_guangzhou.id}/upload/",
                      {"file": f}, format="multipart")
        assert resp.status_code == 400


class TestWeatherQualityCheck:
    """F4-044: 数据质量检查"""

    def test_quality_check_no_missing(self, db, city_guangzhou, engineer_role):
        """连续数据无缺失"""
        create_weather_records(city_guangzhou, 48)
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/weather/{city_guangzhou.id}/quality/")
        assert resp.status_code == 200
        assert resp.data["missing_count"] == 0

    def test_quality_check_detects_gap(self, db, city_guangzhou, engineer_role):
        """检测到时间缺口"""
        base = datetime(2024, 7, 1)
        # 创建第 0 小时和第 5 小时（中间缺口）
        WeatherRecord.objects.create(
            city=city_guangzhou, timestamp=base,
            dry_bulb_temp=Decimal("30"), wet_bulb_temp=Decimal("27"),
        )
        WeatherRecord.objects.create(
            city=city_guangzhou, timestamp=base + timedelta(hours=5),
            dry_bulb_temp=Decimal("30"), wet_bulb_temp=Decimal("27"),
        )
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/weather/{city_guangzhou.id}/quality/")
        assert resp.status_code == 200
        assert resp.data["missing_count"] >= 4  # 缺 4 小时
