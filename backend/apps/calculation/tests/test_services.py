"""核心计算引擎单元测试（PRD §15 权威基线，SAC-2 < 0.1%）

严格 TDD：测试先行，覆盖 C1-C8 全部修复点。
"""
from decimal import Decimal

import pytest

from apps.calculation.services import (
    RHO,
    SEC_PER_HOUR,
    INDOOR_DEFAULT_TEMP,
    INDOOR_DEFAULT_HUMIDITY,
    INFILTRATION_CAP,
    lookup_infiltration_coeff,
    calculate_enthalpy,
    calc_terminal_load,
    calc_air_volume,
    calc_fresh_air_load,
    calc_static,
)


class TestInfiltrationCoefficient:
    """C1: 压差渗透系数 8 点查表（PRD §8.3 唯一权威表）"""

    @pytest.mark.parametrize("pressure_diff,expected", [
        (Decimal("0"), Decimal("0")),
        (Decimal("1"), Decimal("1.0")),
        (Decimal("2"), Decimal("1.5")),
        (Decimal("3"), Decimal("2.0")),
        (Decimal("5"), Decimal("3.0")),
        (Decimal("10"), Decimal("3.5")),
        (Decimal("15"), Decimal("4.0")),
    ])
    def test_table_points(self, pressure_diff, expected):
        """表内点精确匹配"""
        k = lookup_infiltration_coeff(pressure_diff)
        assert abs(k - expected) < Decimal("0.001"), f"|ΔP|={pressure_diff} 期望 k={expected} 实际 k={k}"

    def test_cap_above_15(self):
        """>|±15| 封顶 4.0"""
        assert lookup_infiltration_coeff(Decimal("20")) == INFILTRATION_CAP
        assert lookup_infiltration_coeff(Decimal("100")) == INFILTRATION_CAP

    def test_negative_symmetric(self):
        """负压按绝对值对称（PRD §8.3）"""
        assert lookup_infiltration_coeff(Decimal("-10")) == lookup_infiltration_coeff(Decimal("10"))
        assert lookup_infiltration_coeff(Decimal("-5")) == lookup_infiltration_coeff(Decimal("5"))

    def test_linear_interpolation(self):
        """非表内点线性插值"""
        # 5~10 之间：5→3.0, 10→3.5，7 应为 3.2
        k7 = lookup_infiltration_coeff(Decimal("7"))
        assert abs(k7 - Decimal("3.2")) < Decimal("0.01"), f"7Pa 插值期望 3.2 实际 {k7}"
        # 3~5 之间：3→2.0, 5→3.0，4 应为 2.5
        k4 = lookup_infiltration_coeff(Decimal("4"))
        assert abs(k4 - Decimal("2.5")) < Decimal("0.01")

    def test_none_pressure(self):
        """空值取 0"""
        assert lookup_infiltration_coeff(None) == Decimal("0")

    def test_not_using_sqrt_formula(self):
        """绝不能用 √(ΔP) 或 k=ΔP/5 公式（v1.x 错误实现）"""
        # 10Pa：错误公式给 k=10/5=2 或 √10≈3.16，正确应为 3.5
        assert lookup_infiltration_coeff(Decimal("10")) == Decimal("3.5")
        # 5Pa：错误公式给 k=5/5=1，正确应为 3.0
        assert lookup_infiltration_coeff(Decimal("5")) == Decimal("3.0")


class TestEnthalpy:
    """C3: 焓值计算（psychrolib，SI 单位 kJ/kg）"""

    def test_indoor_standard(self):
        """室内焓值 26°C/55% 应约 55 kJ/kg"""
        h = calculate_enthalpy(Decimal("26"), Decimal("55"), Decimal("1013"), "rh")
        assert Decimal("50") < h < Decimal("62"), f"室内焓值 {h} 超出预期范围"

    def test_outdoor_summer_guangzhou(self):
        """室外焓值 广州 34.2°C干/27.8°C湿 应约 85-92 kJ/kg"""
        h = calculate_enthalpy(Decimal("34.2"), Decimal("27.8"), Decimal("1004"), "wb")
        assert Decimal("80") < h < Decimal("95"), f"室外焓值 {h} 超出预期"

    def test_unit_is_kj_not_j(self):
        """SI 单位制下返回 kJ/kg（已 /1000 修正）"""
        h = calculate_enthalpy(Decimal("25"), Decimal("50"), Decimal("1013"), "rh")
        # 若未除1000，会得到 50000+
        assert h < Decimal("100"), f"焓值 {h} 疑似未转换为 kJ/kg"

    def test_rh_percentage_to_fraction(self):
        """相对湿度 55% 应自动转 0.55（psychrolib 要求 0~1）"""
        h_pct = calculate_enthalpy(Decimal("26"), Decimal("55"), Decimal("1013"), "rh")
        h_frac = calculate_enthalpy(Decimal("26"), Decimal("0.55"), Decimal("1013"), "rh")
        assert abs(h_pct - h_frac) < Decimal("0.01")


class TestTerminalLoad:
    """C5: 末端负荷 5 项（kW 不乘 1000）"""

    def test_five_items(self, room_standard):
        """5 项齐全：土建/照明/人员/电动/电热"""
        result = calc_terminal_load(room_standard)
        assert set(result.keys()) == {"civil", "lighting", "personnel", "electric", "heated", "terminal"}

    def test_civil_load(self, room_standard):
        """土建 = civil_index × area / 1000"""
        result = calc_terminal_load(room_standard)
        expected = Decimal("30") * Decimal("100") / Decimal("1000")  # 3.0 kW
        assert abs(result["civil"] - expected) < Decimal("0.001")

    def test_electric_no_multiply_1000(self, room_standard):
        """电动设备 = power × coeff（kW，不乘1000）"""
        result = calc_terminal_load(room_standard)
        expected = Decimal("10") * Decimal("0.8")  # 8.0 kW
        assert abs(result["electric"] - expected) < Decimal("0.001")

    def test_heated_two_parts(self, room_standard):
        """电热 = 有排风功率×系数 + 无排风功率×系数"""
        result = calc_terminal_load(room_standard)
        expected = Decimal("20") * Decimal("0.7") + Decimal("0") * Decimal("0")  # 14.0 kW
        assert abs(result["heated"] - expected) < Decimal("0.001")

    def test_terminal_sum(self, room_standard):
        """末端 = 五项之和"""
        result = calc_terminal_load(room_standard)
        expected = result["civil"] + result["lighting"] + result["personnel"] + result["electric"] + result["heated"]
        assert abs(result["terminal"] - expected) < Decimal("0.001")

    def test_empty_personnel_is_zero(self, db, floor):
        """人员参数为空按 0 处理"""
        from apps.projects.models import Room
        room = Room.objects.create(
            floor=floor, room_name="无人区", area=Decimal("50"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
        )
        result = calc_terminal_load(room)
        assert result["personnel"] == Decimal("0")


class TestAirVolume:
    """C2: 风量计算（简单加法，无 MAX/卫生/净化）"""

    def test_total_exhaust_sum(self, room_standard):
        """总排风 = 五类排风之和"""
        result = calc_air_volume(room_standard)
        expected = Decimal("500") + Decimal("300") + Decimal("0") + Decimal("0") + Decimal("0")
        assert abs(result["total_exhaust"] - expected) < Decimal("0.01")

    def test_infiltration_uses_lookup(self, room_standard):
        """压差渗透 = volume × k(|ΔP|)"""
        result = calc_air_volume(room_standard)
        # room.volume = 100×3.5 = 350；ΔP=10 → k=3.5
        expected = Decimal("350") * Decimal("3.5")  # 1225 m³/h
        assert abs(result["infiltration"] - expected) < Decimal("0.01")

    def test_fresh_air_simple_addition(self, room_standard):
        """新风量 = 总排风 + 压差渗透（简单加法，无 MAX）"""
        result = calc_air_volume(room_standard)
        expected = result["total_exhaust"] + result["infiltration"]
        assert abs(result["fresh_air"] - expected) < Decimal("0.01")


class TestFreshAirLoad:
    """新风冷负荷（定义A唯一公式，ρ=1.2）"""

    def test_positive_load(self):
        """夏季室外焓 > 室内：正负荷"""
        load = calc_fresh_air_load(Decimal("1000"), Decimal("85"), Decimal("55"))
        expected = RHO * Decimal("1000") * (Decimal("85") - Decimal("55")) / SEC_PER_HOUR
        assert abs(load - expected) < Decimal("0.001")
        assert load > 0

    def test_negative_load_allowed(self):
        """冬季室外焓 < 室内：允许负值"""
        load = calc_fresh_air_load(Decimal("1000"), Decimal("40"), Decimal("55"))
        assert load < 0


class TestCalcStaticIntegration:
    """静态计算全流程集成（PRD §15 6 步流水线）"""

    def test_full_pipeline(self, room_standard):
        """完整计算流程返回所有中间值"""
        result = calc_static(room_standard)
        # 必须包含全部中间结果
        required_keys = {"h_outdoor", "h_indoor", "enthalpy_diff", "civil", "lighting",
                         "personnel", "electric", "heated", "terminal",
                         "total_exhaust", "infiltration", "fresh_air",
                         "fresh_air_load", "total_load"}
        assert required_keys.issubset(result.keys())

    def test_total_truncated_when_negative(self, db, floor, city_guangzhou, building, project):
        """C-截断：总负荷 < 0 时截断为 0"""
        from apps.projects.models import Room
        # 构造新风负负荷远大于末端负荷的场景（冬季工况）
        room = Room.objects.create(
            floor=floor, room_name="极小负荷区", area=Decimal("10"), height=Decimal("2"),
            civil_load_index=Decimal("10"), lighting_load_index=Decimal("5"),
            heat_exhaust_volume=Decimal("10000"),  # 巨大风量
            pressure_diff=Decimal("15"),
            indoor_calc_temp=Decimal("25"), indoor_calc_humidity=Decimal("55"),
        )
        # 调整 city 为冬季低温（室外焓远低于室内）
        city_guangzhou.temp_dry_ac_summer = Decimal("-10")
        city_guangzhou.temp_wet_ac_summer = Decimal("-12")
        city_guangzhou.save()
        result = calc_static(room)
        assert result["total_load"] >= 0, "总负荷应截断为非负"

    def test_cold_index(self, room_standard):
        """冷指标 = total_load / area × 1000 (W/m²)"""
        result = calc_static(room_standard)
        if result["cold_load_index"] is not None:
            expected = result["total_load"] / Decimal("100") * Decimal("1000")
            assert abs(result["cold_load_index"] - expected) < Decimal("0.01")

    def test_default_indoor_temp_humidity(self, db, floor, city_guangzhou, building, project):
        """C4: 室内温湿度为空取默认 26°C/55%"""
        from apps.projects.models import Room
        room = Room.objects.create(
            floor=floor, room_name="默认参数区", area=Decimal("50"), height=Decimal("3"),
            civil_load_index=Decimal("30"), lighting_load_index=Decimal("15"),
            heat_exhaust_volume=Decimal("100"),
            indoor_calc_temp=None, indoor_calc_humidity=None,
        )
        result = calc_static(room)
        # 默认值生效（焓值应接近 26/55 的焓值）
        h_26_55 = calculate_enthalpy(INDOOR_DEFAULT_TEMP, INDOOR_DEFAULT_HUMIDITY, Decimal("1004"), "rh")
        assert abs(result["h_indoor"] - h_26_55) < Decimal("0.5")
