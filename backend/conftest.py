"""pytest 全局 fixtures"""
import pytest
from decimal import Decimal


@pytest.fixture
def engineer_role(db):
    """暖通工程师角色"""
    from apps.accounts.models import Role
    return Role.objects.create(name="engineer", description="暖通工程师")


@pytest.fixture
def city_guangzhou(db):
    """广州城市配置（PRD 附录 C 典型数据）"""
    from apps.common.models import CityConfig
    return CityConfig.objects.create(
        city_name="广州", province="广东", station_code="59287",
        latitude="23°08'", longitude="113°20'", altitude=Decimal("6.6"),
        pressure_summer=Decimal("1004.0"), pressure_winter=Decimal("1019.0"),
        wind_speed_summer=Decimal("1.7"), wind_speed_winter=Decimal("1.7"),
        temp_dry_ac_summer=Decimal("34.2"), temp_wet_ac_summer=Decimal("27.8"),
        temp_dry_ac_winter=Decimal("5.2"), humidity_ac_winter=Decimal("72"),
    )


@pytest.fixture
def project(db, city_guangzhou):
    """示例项目"""
    from apps.projects.models import Project
    return Project.objects.create(
        project_name="广州 PCB 工厂", city=city_guangzhou,
        location="黄埔区XX路", description="测试项目",
    )


@pytest.fixture
def building(db, project):
    from apps.projects.models import Building
    return Building.objects.create(project=project, building_name="1#厂房")


@pytest.fixture
def floor(db, building):
    from apps.projects.models import Floor
    return Floor.objects.create(building=building, floor_name="1F")


@pytest.fixture
def water_temp_mid(db, project):
    """中温冷冻水 12/17°C"""
    from apps.common.models import WaterTempConfig
    return WaterTempConfig.objects.create(
        project=project, temp_type_name="中温冷冻水",
        supply_temp=Decimal("12"), return_temp=Decimal("17"),
    )


@pytest.fixture
def water_temp_low(db, project):
    """低温冷冻水 7/12°C"""
    from apps.common.models import WaterTempConfig
    return WaterTempConfig.objects.create(
        project=project, temp_type_name="低温冷冻水",
        supply_temp=Decimal("7"), return_temp=Decimal("12"),
    )


@pytest.fixture
def room_standard(db, floor):
    """标准功能区域（含完整参数，PRD §6.5）"""
    from apps.projects.models import Room
    return Room.objects.create(
        floor=floor,
        room_name="电镀区",
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
        acid_exhaust_volume=Decimal("300"),
        pressure_diff=Decimal("10"),  # ±10Pa → k=3.5
        indoor_calc_temp=Decimal("25"),
        indoor_calc_humidity=Decimal("55"),
    )
