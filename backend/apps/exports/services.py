"""报告与数据导出 services（F2-032~039 Excel 导入, F8-012~014 CSV 导出）

Excel 导入：按 PRD 附录 A 列映射解析，错误定位到行+字段（F2-035）
CSV 导出：功能区域负荷数据
"""
from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

# PRD 附录 A 列映射（简化版，必填项标注）
REQUIRED_FIELDS = {
    "功能区域名称": "room_name",
    "面积(m²)": "area",
    "吊顶高度(m)": "height",
    "土建指标(W/m²)": "civil_load_index",
    "照明指标(W/m²)": "lighting_load_index",
}
OPTIONAL_FIELDS = {
    "楼层名称": "floor_name",
    "人员指标(W/人)": "personnel_load_index",
    "人数": "personnel_count",
}
ALL_FIELDS = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}


def _to_decimal(val, default=None) -> Decimal | None:
    """安全转 Decimal，空字符串返回 default"""
    if val is None or val == "":
        return default
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return default


def parse_excel_rooms(excel_bytes: bytes) -> dict:
    """解析 Excel，返回功能区域列表 + 错误清单（F2-032~039）

    :return: {success_count, error_count, rooms: [...], errors: [{row, fields, message}]}
    """
    wb = load_workbook(io.BytesIO(excel_bytes), read_only=True, data_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)
    headers = next(rows_iter)
    # 构建列索引
    col_map = {}
    for idx, h in enumerate(headers):
        if h in ALL_FIELDS:
            col_map[h] = idx

    rooms = []
    errors = []
    row_num = 1  # 表头已读

    for row in rows_iter:
        row_num += 1
        record = {}
        missing = []

        for field_cn, field_en in ALL_FIELDS.items():
            col_idx = col_map.get(field_cn)
            val = row[col_idx] if col_idx is not None and col_idx < len(row) else None
            if field_en in ("floor_name", "room_name"):
                record[field_en] = str(val).strip() if val else ""
            elif field_en == "personnel_count":
                record[field_en] = int(val) if val not in (None, "") else None
            else:
                record[field_en] = _to_decimal(val)

        # 必填校验（F2-036）
        for field_cn, field_en in REQUIRED_FIELDS.items():
            val = record.get(field_en)
            if val in (None, "", 0) and field_en != "civil_load_index" and field_en != "lighting_load_index":
                if val == "" or val is None:
                    missing.append(field_cn)
            elif val is None and field_en in ("area", "height", "civil_load_index", "lighting_load_index"):
                missing.append(field_cn)

        # room_name 为空也算缺失
        if not record.get("room_name"):
            if "功能区域名称" not in missing:
                missing.append("功能区域名称")

        if missing:
            errors.append({
                "row": row_num,
                "fields": missing,
                "message": f"必填字段缺失：{', '.join(missing)}",
            })
            continue

        rooms.append(record)

    return {
        "success_count": len(rooms),
        "error_count": len(errors),
        "rooms": rooms,
        "errors": errors,
    }


def export_rooms_csv(rooms: list, calc_results: dict | None = None) -> str:
    """导出功能区域负荷 CSV（F8-012~014）

    :param rooms: Room 实例列表
    :param calc_results: 可选，room_id → RoomCalcResult
    :return: CSV 字符串
    """
    output = io.StringIO()
    output.write("\ufeff")  # BOM for Excel 兼容中文
    writer = csv.writer(output)
    # 表头
    writer.writerow(["功能区域", "楼层", "建筑", "面积(m²)", "末端负荷(kW)",
                     "新风冷负荷(kW)", "总负荷(kW)", "冷指标(W/m²)"])
    for room in rooms:
        building_name = room.floor.building.building_name if room.floor else ""
        floor_name = room.floor.floor_name if room.floor else ""
        row = [
            room.room_name, floor_name, building_name, room.area,
        ]
        if calc_results and room.id in calc_results:
            cr = calc_results[room.id]
            row.extend([cr.terminal_load, cr.fresh_air_volume, cr.total_load, cr.cold_load_index])
        else:
            row.extend(["", "", "", ""])
        writer.writerow(row)

    return output.getvalue()
