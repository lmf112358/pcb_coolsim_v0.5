"""功能区域模型测试（自动计算字段、校验）"""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.projects.models import Room, Project, Building, Floor


class TestRoomAutoCalc:
    """Room.save() 自动计算 volume 与 total_exhaust_volume（PRD §15）"""

    def test_volume_auto_calc(self, floor):
        """volume = area × height"""
        room = Room.objects.create(
            floor=floor, room_name="测试区",
            area=Decimal("100"), height=Decimal("3.5"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        assert room.volume == Decimal("350.00")

    def test_total_exhaust_auto_calc(self, floor):
        """total_exhaust_volume = 五类排风之和"""
        room = Room.objects.create(
            floor=floor, room_name="排风区",
            area=Decimal("50"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
            heat_exhaust_volume=Decimal("100"),
            acid_exhaust_volume=Decimal("200"),
            alkali_exhaust_volume=Decimal("50"),
        )
        assert room.total_exhaust_volume == Decimal("350")

    def test_total_exhaust_all_empty_is_zero(self, floor):
        """排风量全空，total = 0"""
        room = Room.objects.create(
            floor=floor, room_name="无排风",
            area=Decimal("50"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        assert room.total_exhaust_volume == Decimal("0")

    def test_negative_area_rejected(self, floor):
        """面积为负应校验失败"""
        room = Room(
            floor=floor, room_name="非法",
            area=Decimal("-10"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        with pytest.raises(ValidationError):
            room.clean()

    def test_default_status_active(self, floor):
        """默认 status=active"""
        room = Room.objects.create(
            floor=floor, room_name="默认状态",
            area=Decimal("50"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        assert room.status == "active"


class TestProjectCascade:
    """级联删除（PRD §16.1.1）"""

    def test_delete_project_cascades(self, db, city_guangzhou):
        """删除项目级联删除建筑/楼层/功能区域"""
        project = Project.objects.create(project_name="待删", city=city_guangzhou)
        building = Building.objects.create(project=project, building_name="B1")
        floor = Floor.objects.create(building=building, floor_name="1F")
        Room.objects.create(
            floor=floor, room_name="R1", area=Decimal("10"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        project.delete()
        assert not Building.objects.filter(id=building.id).exists()
        assert not Floor.objects.filter(id=floor.id).exists()
        assert Room.objects.count() == 0


class TestExtraLoadLevel:
    """额外负荷层级（F2-030，building_id 区分）"""

    def test_building_level(self, db, project, building):
        """building_id 有值 = 建筑级"""
        from apps.projects.models import ExtraLoad
        load = ExtraLoad.objects.create(
            project=project, building=building,
            category="PCW", load_value=Decimal("100"),
        )
        assert load.building_id is not None

    def test_project_level(self, db, project):
        """building_id 空 = 项目级"""
        from apps.projects.models import ExtraLoad
        load = ExtraLoad.objects.create(
            project=project, building=None,
            category="消防池保温", load_value=Decimal("0.5"),
        )
        assert load.building_id is None
