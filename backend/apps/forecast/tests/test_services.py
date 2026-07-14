"""负荷预测 services 测试（模块十 F10，PRD §14.8/§15.8）

核心：Q(t) = 静态设计负荷 × K(T(t), R(t))
- K 由 RatioCoefficient 表双线性插值（温度区间 × 负荷率）
- PRD §14.8 默认表（5 温度区间 × 5 负荷率）
- 插值示例（PRD §15.8）：20℃/60% → 0.767
"""
from decimal import Decimal

import pytest

from apps.forecast.services import (
    seed_default_coefficients,
    lookup_coefficient,
    bilinear_interpolate,
    forecast_room,
)


@pytest.fixture
def default_coeffs(db):
    """预置 PRD §14.8 默认比例系数表"""
    return seed_default_coefficients()


class TestSeedCoefficients:
    """PRD §14.8 默认系数表预置"""

    def test_seed_creates_25_entries(self, db):
        """5 温度区间 × 5 负荷率 = 25 条"""
        seed_default_coefficients()
        from apps.forecast.models import RatioCoefficient
        assert RatioCoefficient.objects.filter(is_default=True, project__isnull=True).count() == 25

    def test_seed_idempotent(self, db):
        """重复 seed 不重复"""
        seed_default_coefficients()
        seed_default_coefficients()
        from apps.forecast.models import RatioCoefficient
        assert RatioCoefficient.objects.filter(is_default=True).count() == 25

    def test_known_values(self, db):
        """PRD §14.8 权威值核对"""
        seed_default_coefficients()
        from apps.forecast.models import RatioCoefficient
        # <5℃ / 100% → 0.8
        c = RatioCoefficient.objects.get(temp_max=5, rate_percent=100)
        assert c.coefficient == Decimal("0.8")
        # >35℃ / 100% → 1.2
        c = RatioCoefficient.objects.get(temp_min=35, rate_percent=100)
        assert c.coefficient == Decimal("1.2")
        # 25~35℃ / 10% → 0.7
        c = RatioCoefficient.objects.get(temp_min=25, rate_percent=10)
        assert c.coefficient == Decimal("0.7")


class TestLookupCoefficient:
    """系数查表（精确点）"""

    def test_exact_temp_exact_rate(self, default_coeffs):
        """温度和负荷率都在表内：精确返回"""
        k = lookup_coefficient(Decimal("30"), 100)  # 25~35℃ / 100%
        assert k == Decimal("1.1")

    def test_below_5c(self, default_coeffs):
        """<5℃ 区间"""
        k = lookup_coefficient(Decimal("-5"), 100)
        assert k == Decimal("0.8")


class TestBilinearInterpolation:
    """双线性插值（PRD §15.8 示例）"""

    def test_prd_example_20c_60pct(self, default_coeffs):
        """PRD §15.8 示例：20℃/60% → 0.767"""
        k = bilinear_interpolate(Decimal("20"), Decimal("60"))
        # PRD：0.7 + 0.2 × 10/30 ≈ 0.767
        assert abs(k - Decimal("0.7667")) < Decimal("0.005"), f"20℃/60% 实际 {k}"

    def test_exact_point_no_interpolation(self, default_coeffs):
        """精确点不插值"""
        k = bilinear_interpolate(Decimal("30"), Decimal("50"))
        assert k == Decimal("0.9")  # 25~35℃ / 50%

    def test_below_range_clamps(self, default_coeffs):
        """低于表范围用最低行"""
        k = bilinear_interpolate(Decimal("-20"), Decimal("100"))
        assert k == Decimal("0.8")  # <5℃ / 100%

    def test_above_range_clamps(self, default_coeffs):
        """高于表范围用最高行"""
        k = bilinear_interpolate(Decimal("50"), Decimal("100"))
        assert k == Decimal("1.2")  # >35℃ / 100%


class TestForecastRoom:
    """F10-014~017: 功能区域级预测计算"""

    def test_forecast_returns_168_points(self, db, room_standard, default_coeffs):
        """F10-018: 7×24=168 点预测"""
        from apps.forecast.models import ForecastScenario
        import numpy as np
        scenario = ForecastScenario.objects.create(
            project=room_standard.floor.building.project,
            name="测试场景",
            start_date="2024-07-01",
        )
        # 构造 168 小时天气（简化）
        weather_temps = [Decimal("30")] * 168  # 恒温 30℃
        rates = [Decimal("100")] * 168
        results = forecast_room(room_standard, weather_temps, rates)
        assert len(results) == 168

    def test_forecast_uses_static_load(self, db, room_standard, default_coeffs):
        """F10-014: 预测负荷 = 静态设计负荷 × K"""
        from apps.calculation.models import RoomCalcResult
        RoomCalcResult.objects.create(
            room=room_standard, terminal_load=Decimal("10"),
        )
        weather_temps = [Decimal("30")]
        rates = [Decimal("100")]
        results = forecast_room(room_standard, weather_temps, rates)
        # K(30℃,100%) = 1.1
        assert len(results) == 1
        assert abs(results[0] - Decimal("11.0")) < Decimal("0.1")  # 10 × 1.1

    def test_forecast_varies_with_temp(self, db, room_standard, default_coeffs):
        """不同温度产生不同预测负荷"""
        from apps.calculation.models import RoomCalcResult
        RoomCalcResult.objects.create(room=room_standard, terminal_load=Decimal("10"))
        results = forecast_room(
            room_standard,
            [Decimal("0"), Decimal("40")],  # <5℃ vs >35℃
            [Decimal("100"), Decimal("100")],
        )
        assert results[0] != results[1]
