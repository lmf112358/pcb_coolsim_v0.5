"""静态冷量计算引擎（模块四，PRD §15 权威基线）

⚠️ 本模块严格对齐 PRD v0.5.1 §15，不得擅自修改公式：
- 末端负荷 5 项（kW 不乘 1000）
- 压差渗透 8 点查表线性插值（绝不用 k=ΔP/5 或 √ΔP）
- 新风量简单加法（无 MAX/卫生/净化，A4 简化）
- 新风冷负荷 ρ=1.2、定义A唯一公式、室内默认 26°C/55%
- 总负荷 < 0 截断为 0
"""
from decimal import Decimal, getcontext
from typing import Optional

import psychrolib

psychrolib.SetUnitSystem(psychrolib.SI)

# 高精度
getcontext().prec = 28

# 常量（PRD §15.3）
RHO = Decimal("1.2")           # 空气密度 kg/m³（DefaultConfig.air_density 默认值）
SEC_PER_HOUR = Decimal("3600")
INDOOR_DEFAULT_TEMP = Decimal("26")      # 室内默认温度 °C（F4-011）
INDOOR_DEFAULT_HUMIDITY = Decimal("55")  # 室内默认湿度 %（F4-011，不是60%）

# PRD §8.3 压差渗透系数唯一权威表（8 点，正负压对称取绝对值）
# 绝不能用 k = pressure_diff / 5 或 k = √(ΔP) 公式（v1.x 错误实现已删除）
INFILTRATION_TABLE = [
    (Decimal("0"), Decimal("0")),
    (Decimal("1"), Decimal("1.0")),
    (Decimal("2"), Decimal("1.5")),
    (Decimal("3"), Decimal("2.0")),
    (Decimal("5"), Decimal("3.0")),
    (Decimal("10"), Decimal("3.5")),
    (Decimal("15"), Decimal("4.0")),
]
INFILTRATION_CAP = Decimal("4.0")  # >|±15| 封顶


def lookup_infiltration_coeff(pressure_diff: Decimal | None) -> Decimal:
    """压差渗透系数 k：8 点查表线性插值（PRD §8.3）

    正/负压按绝对值对称；>|±15| 封顶 4.0。
    """
    if pressure_diff is None:
        return Decimal("0")
    x = abs(pressure_diff)
    if x >= Decimal("15"):
        return INFILTRATION_CAP
    # 线性插值
    for i in range(len(INFILTRATION_TABLE) - 1):
        x0, y0 = INFILTRATION_TABLE[i]
        x1, y1 = INFILTRATION_TABLE[i + 1]
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return Decimal("0")


def calculate_enthalpy(temp_dry: Decimal, humidity: Decimal, pressure_hpa: Decimal,
                       input_type: str = "rh") -> Decimal:
    """焓值计算（psychrolib，PRD §15.3）

    :param input_type: 'rh' 相对湿度 / 'wb' 湿球温度
    """
    p_pa = float(pressure_hpa) * 100
    t = float(temp_dry)
    if input_type == "rh":
        # psychrolib 相对湿度要求 0~1 小数；业务层传入 0~100 百分比（PRD 55%）
        rh = float(humidity)
        if rh > 1:  # 容错：>1 视为百分比，转换为小数
            rh = rh / 100
        hr = psychrolib.GetHumRatioFromRelHum(t, rh, p_pa)
    else:  # wb 湿球
        hr = psychrolib.GetHumRatioFromTWetBulb(t, float(humidity), p_pa)
    # 注意：本版本 GetMoistAirEnthalpy 只接受 (TDryBulb, HumRatio)，无需 pressure；
    # SI 单位制下返回 J/kg，需 /1000 转 kJ/kg（PRD §15.3）
    h = psychrolib.GetMoistAirEnthalpy(t, hr) / 1000
    return Decimal(str(h))


def _or_zero(v) -> Decimal:
    """空值取 0（PRD：人员/设备参数为空按 0 处理）"""
    if v is None:
        return Decimal("0")
    return v


def calc_terminal_load(room) -> dict[str, Decimal]:
    """末端负荷 5 项（PRD §15.1，kW 不乘 1000）

    返回 dict：civil/lighting/personnel/electric/heated/terminal
    """
    civil = room.civil_load_index * room.area / Decimal("1000")
    lighting = room.lighting_load_index * room.area / Decimal("1000")
    personnel = _or_zero(room.personnel_load_index) * _or_zero(room.personnel_count) / Decimal("1000")
    electric = _or_zero(room.electric_equipment_power) * _or_zero(room.electric_equipment_coefficient)
    heated = (
        _or_zero(room.heated_equipment_power_with_exhaust) * _or_zero(room.heated_equipment_coefficient_with_exhaust)
        + _or_zero(room.heated_equipment_power_without_exhaust) * _or_zero(room.heated_equipment_coefficient_without_exhaust)
    )
    terminal = civil + lighting + personnel + electric + heated
    return {
        "civil": civil, "lighting": lighting, "personnel": personnel,
        "electric": electric, "heated": heated, "terminal": terminal,
    }


def calc_air_volume(room) -> dict[str, Decimal]:
    """风量计算（PRD §15.2，简单加法，无 MAX/卫生/净化）

    返回 dict：total_exhaust/infiltration/fresh_air
    """
    total_exhaust = sum(filter(None, [
        room.heat_exhaust_volume, room.acid_exhaust_volume,
        room.alkali_exhaust_volume, room.organic_exhaust_volume,
        room.dust_exhaust_volume,
    ]), Decimal("0"))
    k = lookup_infiltration_coeff(room.pressure_diff)
    infiltration = _or_zero(room.volume) * k
    fresh_air = total_exhaust + infiltration  # 简单加法（A4）
    return {"total_exhaust": total_exhaust, "infiltration": infiltration, "fresh_air": fresh_air}


def calc_fresh_air_load(fresh_air_volume: Decimal, h_outdoor: Decimal, h_indoor: Decimal) -> Decimal:
    """新风冷负荷（PRD §15.3 定义A唯一公式）

    Q_fresh = ρ × V × (h_out − h_in) / 3600，可为负。
    """
    return RHO * fresh_air_volume * (h_outdoor - h_indoor) / SEC_PER_HOUR


def calc_static(room) -> dict:
    """静态冷量计算全流程（PRD §15，6 步流水线骨架）

    返回完整计算结果 dict，供 RoomCalcResult/RoomLoadByWaterTemp 落库。
    注：按水温分类（ADR-0001）与多级汇总由调用方在落库时处理。
    """
    # Step 1 焓值
    indoor_t = _or_zero(room.indoor_calc_temp) or INDOOR_DEFAULT_TEMP
    indoor_h = _or_zero(room.indoor_calc_humidity) or INDOOR_DEFAULT_HUMIDITY
    city = room.floor.building.project.city
    h_outdoor = calculate_enthalpy(
        city.temp_dry_ac_summer, city.temp_wet_ac_summer, city.pressure_summer, "wb"
    )
    h_indoor = calculate_enthalpy(indoor_t, indoor_h, city.pressure_summer, "rh")

    # Step 2 末端负荷（Q_terminal 桥梁）
    terminal = calc_terminal_load(room)

    # Step 3 风量
    air = calc_air_volume(room)

    # Step 4 新风冷负荷（定义A，可为负）
    fresh_load = calc_fresh_air_load(air["fresh_air"], h_outdoor, h_indoor)

    # Step 5 总负荷（<0 截断为0，与动态统一）
    total = terminal["terminal"] + fresh_load
    if total < 0:
        total = Decimal("0")

    return {
        "h_outdoor": h_outdoor, "h_indoor": h_indoor, "enthalpy_diff": h_outdoor - h_indoor,
        **terminal,
        **air,
        "fresh_air_load": fresh_load,
        "total_load": total,
        "cold_load_index": total / room.area * Decimal("1000") if room.area else None,
    }
