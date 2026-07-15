"""NF-SAC-04 性能基准测试（PRD §17.1：1000+ 功能区域静态计算 <5s）

用批量创建的 1000 个功能区域测试静态计算性能。
"""
import time
from decimal import Decimal

import pytest

from apps.calculation.services import calc_static
from apps.projects.models import Room


def create_rooms_bulk(floor, count=1000):
    """批量创建 count 个功能区域"""
    rooms = []
    for i in range(count):
        rooms.append(Room(
            floor=floor,
            room_name=f"测试区域_{i:04d}",
            area=Decimal("100"),
            height=Decimal("3.5"),
            civil_load_index=Decimal("30"),
            lighting_load_index=Decimal("15"),
            personnel_load_index=Decimal("60"),
            personnel_count=5,
            electric_equipment_power=Decimal("10"),
            electric_equipment_coefficient=Decimal("0.8"),
            heated_equipment_power_with_exhaust=Decimal("20"),
            heated_equipment_coefficient_with_exhaust=Decimal("0.7"),
            heat_exhaust_volume=Decimal("500"),
            pressure_diff=Decimal("10"),
            indoor_calc_temp=Decimal("25"),
            indoor_calc_humidity=Decimal("55"),
        ))
    Room.objects.bulk_create(rooms)
    return rooms


@pytest.mark.django_db
class TestPerformanceNF004:
    """NF-SAC-04: 静态冷量计算 1000+ 功能区域 <5s"""

    def test_calc_1000_rooms_under_5_seconds(self, city_guangzhou, building, floor):
        """PRD F4-028/NF-005: 1000 个功能区域静态计算 < 5 秒"""
        # 批量创建 1000 个功能区域
        rooms = create_rooms_bulk(floor, 1000)
        assert Room.objects.count() == 1000

        # 计时执行
        start = time.time()
        for room in rooms:
            calc_static(room)
        elapsed = time.time() - start

        print(f"\n1000 个功能区域静态计算耗时: {elapsed:.2f}s")
        # NF-SAC-04 要求 < 5s
        assert elapsed < 5.0, f"性能不达标: {elapsed:.2f}s >= 5s (NF-SAC-04)"

    def test_calc_100_rooms_smoke(self, city_guangzhou, building, floor):
        """100 个功能区域冒烟测试"""
        rooms = create_rooms_bulk(floor, 100)
        start = time.time()
        for room in rooms:
            result = calc_static(room)
            assert result["terminal"] > 0
        elapsed = time.time() - start
        print(f"\n100 个功能区域耗时: {elapsed:.2f}s")
        assert elapsed < 1.0
