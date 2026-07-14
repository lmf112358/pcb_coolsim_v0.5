"""负荷预测计算引擎（模块十 F10，PRD §14.8/§15.8）

核心：Q(t) = 静态设计负荷 × K(T(t), R(t))
- K 由 RatioCoefficient 表双线性插值（温度区间 × 负荷率）
- PRD §14.8 默认表：5 温度区间（<5/5~15/15~25/25~35/>35）× 5 负荷率（10/30/50/80/100）
- 插值示例（PRD §15.8）：20℃/60% → 0.767
"""
from decimal import Decimal

from apps.forecast.models import RatioCoefficient

# PRD §14.8 默认系数表（系统默认值，须暖通工程师校准确认）
DEFAULT_TABLE = {
    # temp_range: (min, max)
    # rate_percent: coefficient
    "rows": [
        # (temp_min, temp_max, {rate: coeff})
        (Decimal("-999"), Decimal("5"), {10: Decimal("0.3"), 30: Decimal("0.4"), 50: Decimal("0.5"), 80: Decimal("0.7"), 100: Decimal("0.8")}),
        (Decimal("5"), Decimal("15"), {10: Decimal("0.4"), 30: Decimal("0.5"), 50: Decimal("0.6"), 80: Decimal("0.8"), 100: Decimal("0.9")}),
        (Decimal("15"), Decimal("25"), {10: Decimal("0.5"), 30: Decimal("0.6"), 50: Decimal("0.7"), 80: Decimal("0.9"), 100: Decimal("1.0")}),
        (Decimal("25"), Decimal("35"), {10: Decimal("0.7"), 30: Decimal("0.8"), 50: Decimal("0.9"), 80: Decimal("1.0"), 100: Decimal("1.1")}),
        (Decimal("35"), Decimal("999"), {10: Decimal("0.8"), 30: Decimal("0.9"), 50: Decimal("1.0"), 80: Decimal("1.1"), 100: Decimal("1.2")}),
    ]
}

RATE_LEVELS = [10, 30, 50, 80, 100]


def seed_default_coefficients(project=None) -> int:
    """预置 PRD §14.8 默认系数表到 RatioCoefficient

    :param project: 项目级覆盖时传入；None=系统默认
    :return: 创建/更新的条数
    """
    count = 0
    for temp_min, temp_max, rate_map in DEFAULT_TABLE["rows"]:
        for rate, coeff in rate_map.items():
            RatioCoefficient.objects.update_or_create(
                temp_min=temp_min, temp_max=temp_max,
                rate_percent=rate, project=project,
                defaults={"coefficient": coeff, "is_default": project is None},
            )
            count += 1
    return count


def _find_temp_row(temp: Decimal) -> tuple[Decimal, Decimal, dict]:
    """定位温度所在行"""
    for temp_min, temp_max, rate_map in DEFAULT_TABLE["rows"]:
        if temp_min <= temp < temp_max:
            return temp_min, temp_max, rate_map
    # 低于最低/高于最高：夹取首/末行
    if temp < DEFAULT_TABLE["rows"][0][0]:
        return DEFAULT_TABLE["rows"][0][0], DEFAULT_TABLE["rows"][0][1], DEFAULT_TABLE["rows"][0][2]
    last = DEFAULT_TABLE["rows"][-1]
    return last[0], last[1], last[2]


def lookup_coefficient(temp: Decimal, rate_percent: int) -> Decimal:
    """查表（精确温度区间 + 精确负荷率）"""
    _, _, rate_map = _find_temp_row(temp)
    if rate_percent in rate_map:
        return rate_map[rate_percent]
    # 不在标准负荷率，用最近邻
    closest = min(RATE_LEVELS, key=lambda r: abs(r - rate_percent))
    return rate_map[closest]


def bilinear_interpolate(temp: Decimal, rate: Decimal) -> Decimal:
    """双线性插值（PRD §15.8）

    温度维度：所在区间内的位置
    负荷率维度：两个相邻负荷率之间
    """
    # 1. 温度维度：找到所在行和下一行（用于温度插值）
    rows = DEFAULT_TABLE["rows"]
    row_idx = 0
    for i, (tmin, tmax, _) in enumerate(rows):
        if tmin <= temp < tmax:
            row_idx = i
            break
    else:
        # 超范围：夹取
        if temp < rows[0][0]:
            row_idx = 0
        else:
            row_idx = len(rows) - 1

    temp_min, temp_max, rate_map = rows[row_idx]

    # 温度在区间内不需要温度向插值（PRD §15.8 示例只在负荷率维度插值）
    # 找两个相邻负荷率
    lower_rate = max(r for r in RATE_LEVELS if r <= rate)
    upper_rate = min(r for r in RATE_LEVELS if r >= rate)
    if lower_rate == upper_rate:
        return rate_map[lower_rate]

    k_low = rate_map[lower_rate]
    k_high = rate_map[upper_rate]
    # 线性插值（PRD §15.8 示例公式）
    k = k_low + (k_high - k_low) * (rate - Decimal(lower_rate)) / Decimal(upper_rate - lower_rate)
    return k.quantize(Decimal("0.0001"))


def forecast_room(room, weather_temps: list[Decimal], rates: list[Decimal]) -> list[Decimal]:
    """功能区域级预测计算（F10-014~017）

    Q(t) = 静态设计负荷 × K(T(t), R(t))
    静态设计负荷取 RoomCalcResult.terminal_load（无结果则取 0）。
    """
    from apps.calculation.models import RoomCalcResult

    try:
        calc = RoomCalcResult.objects.get(room=room)
        static_load = calc.terminal_load
    except RoomCalcResult.DoesNotExist:
        static_load = Decimal("0")

    results = []
    for temp, rate in zip(weather_temps, rates):
        k = bilinear_interpolate(temp, rate)
        predicted = static_load * k
        results.append(predicted.quantize(Decimal("0.0001")))
    return results
