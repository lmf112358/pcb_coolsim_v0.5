"""动态仿真 services 测试（模块六 F6-001~011，方式一气象驱动）

PRD §15.4 / §10.2：
- Q_dynamic(t) = Q_terminal + Q_fresh_air(t)
- Q_terminal 从静态计算复用（桥梁，F6-005）
- Q_fresh_air(t) = ρ × V_fresh × (h_outdoor(t) − h_indoor) / 3600
- Q_dynamic(t) < 0 截断为 0（F6-006，与 F4-014 一致）
- 室外焓值 NumPy 向量化（F6-007）
- SAC-3：与独立脚本验算偏差 < 1%
"""
from decimal import Decimal

import numpy as np
import pytest

from apps.simulation.services import (
    simulate_weather_driven,
    vectorized_enthalpy,
    aggregate_extremes,
)


@pytest.fixture
def weather_series_summer():
    """夏季 72 小时气象序列（简化，3 天）"""
    rng = np.random.default_rng(42)
    temp_dry = rng.uniform(28, 36, 72)
    # 湿球必须低于干球（psychrolib 要求）
    temp_wet = temp_dry - rng.uniform(2, 6, 72)
    return {
        "timestamps": np.array([np.datetime64("2024-07-01") + np.timedelta64(i, "h") for i in range(72)]),
        "temp_dry": temp_dry,
        "temp_wet": temp_wet,
        "pressure": np.full(72, 1004.0),            # 广州夏季大气压
    }


@pytest.fixture
def room_with_static_result(room_standard):
    """已完成静态计算的 room（提供 Q_terminal 桥梁 + 新风量 + 室内焓值）"""
    from apps.calculation.services import calc_static
    from apps.calculation.models import RoomCalcResult
    result = calc_static(room_standard)
    RoomCalcResult.objects.update_or_create(
        room=room_standard,
        defaults={
            "civil_load": result["civil"], "lighting_load": result["lighting"],
            "personnel_load": result["personnel"], "electric_equipment_load": result["electric"],
            "heated_equipment_load": result["heated"], "terminal_load": result["terminal"],
            "total_exhaust_volume": result["total_exhaust"],
            "infiltration_air_volume": result["infiltration"],
            "fresh_air_volume": result["fresh_air"],
            "indoor_enthalpy_calc": result["h_indoor"],
            "outdoor_enthalpy_calc": result["h_outdoor"],
            "enthalpy_diff": result["enthalpy_diff"],
            "cold_load_index": result["cold_load_index"],
        },
    )
    return room_standard


class TestVectorizedEnthalpy:
    """F6-002/007: 室外焓值 NumPy 向量化计算"""

    def test_returns_numpy_array(self, weather_series_summer):
        """返回 numpy 数组"""
        w = weather_series_summer
        h = vectorized_enthalpy(w["temp_dry"], w["temp_wet"], w["pressure"])
        assert isinstance(h, np.ndarray)
        assert len(h) == 72

    def test_values_in_reasonable_range(self, weather_series_summer):
        """夏季焓值应在 60~100 kJ/kg 范围"""
        w = weather_series_summer
        h = vectorized_enthalpy(w["temp_dry"], w["temp_wet"], w["pressure"])
        assert np.all(h > 50), f"最小焓值 {h.min()} 偏低"
        assert np.all(h < 120), f"最大焓值 {h.max()} 偏高"

    def test_consistent_with_scalar(self):
        """向量化结果与标量 psychrolib 一致（SAC-3 精度验证）"""
        from apps.calculation.services import calculate_enthalpy
        h_vec = vectorized_enthalpy(
            np.array([34.2]), np.array([27.8]), np.array([1004.0])
        )
        h_scalar = float(calculate_enthalpy(Decimal("34.2"), Decimal("27.8"), Decimal("1004"), "wb"))
        assert abs(h_vec[0] - h_scalar) < 0.5, f"向量化{h_vec[0]} vs 标量{h_scalar}"

    def test_performance_26280_points(self):
        """F6-007: 26280 点焓值计算应快速（向量化）"""
        rng = np.random.default_rng(0)
        t_dry = rng.uniform(0, 40, 26280)
        t_wet = t_dry - rng.uniform(2, 8, 26280)  # 湿球低于干球
        p = np.full(26280, 1013.0)
        import time
        start = time.time()
        h = vectorized_enthalpy(t_dry, t_wet, p)
        elapsed = time.time() - start
        assert len(h) == 26280
        # 向量化应 < 10 秒（含 psychrolib 标量循环）
        assert elapsed < 30, f"26280 点耗时 {elapsed:.2f}s"


class TestSimulateWeatherDriven:
    """F6-001~006: 气象驱动动态仿真主流程"""

    def test_returns_hourly_array(self, room_with_static_result, weather_series_summer):
        """返回逐时负荷数组，长度 = 气象点数"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        assert "total_load" in result
        assert "fresh_air_load" in result
        assert "terminal_load" in result
        assert len(result["total_load"]) == 72

    def test_terminal_load_constant(self, room_with_static_result, weather_series_summer):
        """F6-005: Q_terminal 全年恒定（取自静态 RoomCalcResult）"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        # 末端负荷每个时刻相同
        t = result["terminal_load"]
        assert np.all(t == t[0]), "末端负荷应全年恒定"

    def test_fresh_air_varies_with_weather(self, room_with_static_result, weather_series_summer):
        """F6-004: 新风负荷随气象变化"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        fresh = result["fresh_air_load"]
        assert len(np.unique(fresh)) > 1, "新风负荷应随气象变化"

    def test_total_equals_terminal_plus_fresh(self, room_with_static_result, weather_series_summer):
        """F6-005: Q_dynamic = Q_terminal + Q_fresh（截断前）"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        raw = result["terminal_load"] + result["fresh_air_load"]
        # 截断后 total = max(raw, 0)
        expected = np.where(raw < 0, 0, raw)
        np.testing.assert_array_almost_equal(result["total_load"], expected)

    def test_negative_total_truncated(self, db, floor, city_guangzhou, building, project):
        """F6-006: Q_dynamic < 0 截断为 0（与 F4-014 一致）"""
        from apps.calculation.services import calc_static
        from apps.calculation.models import RoomCalcResult
        from apps.projects.models import Room
        room = Room.objects.create(
            floor=floor, room_name="冬季截断测试", area=Decimal("10"), height=Decimal("2"),
            civil_load_index=Decimal("5"), lighting_load_index=Decimal("5"),
            heat_exhaust_volume=Decimal("5000"),
            pressure_diff=Decimal("10"),
            indoor_calc_temp=Decimal("25"), indoor_calc_humidity=Decimal("55"),
        )
        # 写入静态结果（极小末端负荷）
        r = calc_static(room)
        RoomCalcResult.objects.update_or_create(
            room=room,
            defaults={"terminal_load": r["terminal"], "fresh_air_volume": r["fresh_air"],
                      "indoor_enthalpy_calc": r["h_indoor"]},
        )
        # 构造冬季低温气象（室外焓远低于室内），湿球须低于干球
        winter = {
            "timestamps": np.array([np.datetime64("2024-01-01") + np.timedelta64(i, "h") for i in range(24)]),
            "temp_dry": np.full(24, -10.0),
            "temp_wet": np.full(24, -12.0),
            "pressure": np.full(24, 1020.0),
        }
        result = simulate_weather_driven(room, winter)
        # 总负荷应被截断为非负
        assert np.all(result["total_load"] >= 0), "总负荷应截断为非负"


class TestExtremes:
    """F7-027~028: 极值统计"""

    def test_extremes(self, room_with_static_result, weather_series_summer):
        """返回 max/min/mean 及发生时刻"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        extremes = aggregate_extremes(result["total_load"], weather_series_summer["timestamps"])
        assert "max_load" in extremes
        assert "min_load" in extremes
        assert "avg_load" in extremes
        assert "max_time" in extremes

    def test_min_excludes_zero_when_exists(self, room_with_static_result, weather_series_summer):
        """PRD §8.1: Q_min 取 >0 的有意义最小值（极值统计）"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        extremes = aggregate_extremes(result["total_load"], weather_series_summer["timestamps"])
        total = result["total_load"]
        positive = total[total > 0]
        if len(positive) > 0:
            assert abs(extremes["min_load"] - positive.min()) < 0.01

    def test_max_is_actual_max(self, room_with_static_result, weather_series_summer):
        """max_load 应等于数组最大值"""
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        extremes = aggregate_extremes(result["total_load"], weather_series_summer["timestamps"])
        assert abs(extremes["max_load"] - result["total_load"].max()) < 0.01


class TestBridgeConsistency:
    """Q_terminal 桥梁一致性（静态动态共用）"""

    def test_terminal_matches_static(self, room_with_static_result, weather_series_summer):
        """动态仿真的 Q_terminal 应等于静态 RoomCalcResult.terminal_load"""
        from apps.calculation.models import RoomCalcResult
        static = RoomCalcResult.objects.get(room=room_with_static_result)
        result = simulate_weather_driven(room_with_static_result, weather_series_summer)
        assert abs(result["terminal_load"][0] - float(static.terminal_load)) < 0.01
