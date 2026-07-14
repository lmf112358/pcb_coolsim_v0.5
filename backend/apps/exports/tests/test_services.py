"""Excel 导入与 CSV 导出 services 测试（F2-032~039, F8-012~014）"""
from decimal import Decimal
from io import BytesIO

import pytest
from openpyxl import Workbook

from apps.exports.services import parse_excel_rooms, export_rooms_csv


def make_test_excel(rows: list[dict]) -> bytes:
    """构造测试 Excel（PRD 附录A 列结构）"""
    wb = Workbook()
    ws = wb.active
    ws.title = "功能区域"
    # 表头（PRD 附录A 列映射）
    headers = ["楼层名称", "功能区域名称", "面积(m²)", "吊顶高度(m)",
               "土建指标(W/m²)", "照明指标(W/m²)", "人员指标(W/人)", "人数"]
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h, "") for h in headers])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestExcelImport:
    """F2-032~039: Excel 批量导入"""

    def test_parse_valid_rows(self):
        """解析有效行"""
        excel = make_test_excel([
            {"楼层名称": "1F", "功能区域名称": "曝光区", "面积(m²)": 100, "吊顶高度(m)": 3.5,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": 60, "人数": 5},
            {"楼层名称": "1F", "功能区域名称": "电镀区", "面积(m²)": 200, "吊顶高度(m)": 4,
             "土建指标(W/m²)": 35, "照明指标(W/m²)": 20, "人员指标(W/人)": 60, "人数": 8},
        ])
        result = parse_excel_rooms(excel)
        assert result["success_count"] == 2
        assert result["error_count"] == 0
        assert len(result["errors"]) == 0
        assert len(result["rooms"]) == 2

    def test_required_field_missing(self):
        """F2-036: 必填校验"""
        excel = make_test_excel([
            {"楼层名称": "1F", "功能区域名称": "", "面积(m²)": 100, "吊顶高度(m)": 3.5,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": 60, "人数": 5},
        ])
        result = parse_excel_rooms(excel)
        assert result["success_count"] == 0
        assert result["error_count"] == 1
        assert result["errors"][0]["row"] == 2  # 第2行（表头是第1行）

    def test_error_locates_row_and_field(self):
        """F2-035: 错误定位到行和字段"""
        excel = make_test_excel([
            {"楼层名称": "1F", "功能区域名称": "曝光区", "面积(m²)": 100, "吊顶高度(m)": 3.5,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": 60, "人数": 5},
            {"楼层名称": "2F", "功能区域名称": "空面积", "面积(m²)": "", "吊顶高度(m)": 3.5,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": 60, "人数": 5},
        ])
        result = parse_excel_rooms(excel)
        assert result["errors"][0]["row"] == 3
        assert "面积" in str(result["errors"][0]["fields"])

    def test_parses_decimal_values(self):
        """数值正确解析为 Decimal"""
        excel = make_test_excel([
            {"楼层名称": "1F", "功能区域名称": "区A", "面积(m²)": 120.5, "吊顶高度(m)": 3.5,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": 60, "人数": 5},
        ])
        result = parse_excel_rooms(excel)
        room = result["rooms"][0]
        assert room["area"] == Decimal("120.5")
        assert room["height"] == Decimal("3.5")

    def test_builds_floor_hierarchy(self):
        """F2-034: 自动建立楼层→功能区域层级"""
        excel = make_test_excel([
            {"楼层名称": "1F", "功能区域名称": "区A", "面积(m²)": 100, "吊顶高度(m)": 3,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": "", "人数": ""},
            {"楼层名称": "2F", "功能区域名称": "区B", "面积(m²)": 100, "吊顶高度(m)": 3,
             "土建指标(W/m²)": 30, "照明指标(W/m²)": 15, "人员指标(W/人)": "", "人数": ""},
        ])
        result = parse_excel_rooms(excel)
        floors = {r["floor_name"] for r in result["rooms"]}
        assert floors == {"1F", "2F"}


class TestCsvExport:
    """F8-012~014: CSV 导出"""

    def test_export_csv_header(self, db, room_standard):
        """CSV 含正确表头"""
        csv_content = export_rooms_csv([room_standard])
        lines = csv_content.strip().split("\n")
        assert "时间戳" in lines[0] or "room_name" in lines[0] or "功能区域" in lines[0]

    def test_export_csv_content(self, db, room_standard):
        """CSV 含功能区域数据行"""
        csv_content = export_rooms_csv([room_standard])
        assert room_standard.room_name in csv_content

    def test_export_csv_empty_rooms(self, db):
        """空列表导出只含表头"""
        csv_content = export_rooms_csv([])
        lines = csv_content.strip().split("\n")
        assert len(lines) == 1  # 仅表头
