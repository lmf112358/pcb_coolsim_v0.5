"""报告导出 API 测试（F8-001~014）"""
import pytest
from rest_framework.test import APIClient


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="exuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestExportAPI:
    """F8-001~014 报告与数据导出"""

    def test_export_static_report_csv(self, db, room_standard, engineer_role):
        """F8-001/012: 导出静态计算结果 CSV"""
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/exports/rooms-csv/?floor_id={room_standard.floor_id}")
        assert resp.status_code == 200
        assert "text/csv" in resp["Content-Type"]
        # CSV 含功能区域名
        content = resp.content.decode("utf-8-sig")
        assert room_standard.room_name in content

    def test_export_pdf_report(self, db, project, engineer_role):
        """F8-001~004: 导出 PDF 报告"""
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/exports/pdf-report/{project.id}/")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"

    def test_export_excel_template(self, db, engineer_role):
        """F8/附录A: 下载 Excel 导入模板"""
        c = auth_client(db, engineer_role)
        resp = c.get("/api/v1/exports/excel-template/")
        assert resp.status_code == 200
        # Excel MIME 类型
        ct = resp["Content-Type"]
        assert "spreadsheet" in ct or "excel" in ct or "octet" in ct

    def test_export_requires_auth(self, db, project):
        """未认证 401"""
        c = APIClient()
        resp = c.get(f"/api/v1/exports/pdf-report/{project.id}/")
        assert resp.status_code == 401

    def test_import_excel(self, db, floor, engineer_role):
        """F2-032~039: Excel 批量导入端点"""
        from io import BytesIO
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["楼层名称", "功能区域名称", "面积(m²)", "吊顶高度(m)",
                   "土建指标(W/m²)", "照明指标(W/m²)", "人员指标(W/人)", "人数"])
        ws.append(["1F", "导入区", 100, 3.5, 30, 15, 60, 5])
        buf = BytesIO()
        wb.save(buf)
        c = auth_client(db, engineer_role)
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("test.xlsx", buf.getvalue(),
                               content_type="application/vnd.openxmlformats")
        resp = c.post(f"/api/v1/exports/import-excel/?floor_id={floor.building_id}",
                      {"file": f}, format="multipart")
        assert resp.status_code in (200, 201)
