"""动态仿真负荷计算引擎（模块六 F6-001~023，PRD §15.4 / §10.2）

方式一：气象数据驱动
  Q_dynamic(t) = Q_terminal + Q_fresh_air(t)
  Q_terminal 全年恒定（从静态 RoomCalcResult 复用，桥梁 F6-005）
  Q_fresh_air(t) = ρ × V_fresh × (h_outdoor(t) − h_indoor) / 3600
  Q_dynamic(t) < 0 截断为 0（F6-006，与 F4-014 一致）

室外焓值用 NumPy 向量化（F6-007，26280 次 < 1s 量级）。
"""
from __future__ import annotations

import numpy as np
import psychrolib

from apps.calculation.services import RHO, SEC_PER_HOUR

psychrolib.SetUnitSystem(psychrolib.SI)


def vectorized_enthalpy(
    temp_dry: np.ndarray,
    temp_wet: np.ndarray,
    pressure_hpa: np.ndarray,
) -> np.ndarray:
    """室外焓值向量化计算（F6-002/007）

    用湿球温度推算含湿量，再算焓值。返回 kJ/kg（已 /1000）。
    psychrolib 是标量库，用 np.vectorize 包装实现批量（语法糖，非真向量化，
    但 26280 次在秒级完成，满足 F6-007）。
    """
    p_pa = pressure_hpa * 100.0

    def _scalar(t_db: float, t_wb: float, p: float) -> float:
        hr = psychrolib.GetHumRatioFromTWetBulb(t_db, t_wb, p)
        return psychrolib.GetMoistAirEnthalpy(t_db, hr) / 1000.0

    vec = np.vectorize(_scalar)
    return vec(temp_dry, temp_wet, p_pa)


def simulate_weather_driven(room, weather: dict) -> dict:
    """气象驱动动态仿真主流程（F6-001~006）

    :param room: Room 实例（需有关联的 RoomCalcResult）
    :param weather: dict 含 timestamps/temp_dry/temp_wet/pressure（numpy 数组）
    :return: dict 含 total_load/fresh_air_load/terminal_load（numpy 数组）
    """
    from apps.calculation.models import RoomCalcResult

    # Q_terminal 桥梁：从静态结果取（F6-005）
    try:
        calc = RoomCalcResult.objects.get(room=room)
    except RoomCalcResult.DoesNotExist:
        raise ValueError(
            f"功能区域 {room.id} 未完成静态计算，请先执行静态计算（Q_terminal 桥梁）"
        )

    q_terminal = float(calc.terminal_load)
    v_fresh = float(calc.fresh_air_volume or 0)
    h_indoor = float(calc.indoor_enthalpy_calc or 0)

    n = len(weather["temp_dry"])
    # 逐时室外焓值（向量化，F6-002/007）
    h_outdoor = vectorized_enthalpy(
        weather["temp_dry"], weather["temp_wet"], weather["pressure"]
    )

    # 逐时新风负荷（F6-004）：可为负
    rho = float(RHO)
    sec = float(SEC_PER_HOUR)
    q_fresh = rho * v_fresh * (h_outdoor - h_indoor) / sec

    # 末端负荷全年恒定（F6-003/005）
    q_term = np.full(n, q_terminal, dtype=float)

    # 总负荷 = 末端 + 新风（F6-005），< 0 截断（F6-006）
    raw = q_term + q_fresh
    q_total = np.where(raw < 0, 0.0, raw)

    return {
        "total_load": q_total,
        "fresh_air_load": q_fresh,
        "terminal_load": q_term,
        "outdoor_enthalpy": h_outdoor,
    }


def aggregate_extremes(total_load: np.ndarray, timestamps: np.ndarray) -> dict:
    """极值统计（F7-027~028）

    Q_min 取 > 0 的有意义最小值（PRD §8.1，与 F4-014 截断规则一致）。
    """
    positive = total_load[total_load > 0]
    max_idx = int(np.argmax(total_load))
    if len(positive) > 0:
        min_val = float(positive.min())
    else:
        min_val = 0.0

    return {
        "max_load": float(total_load.max()),
        "min_load": min_val,
        "avg_load": float(total_load.mean()),
        "max_time": str(timestamps[max_idx]) if max_idx < len(timestamps) else None,
    }
