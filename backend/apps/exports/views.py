"""报告导出 API 视图（F8-001~014）"""
from io import BytesIO

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Project, Floor, Room
from apps.exports.services import export_rooms_csv, parse_excel_rooms


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_rooms_csv_view(request):
    """F8-012: 导出功能区域 CSV"""
    floor_id = request.query_params.get("floor_id")
    rooms = Room.objects.all()
    if floor_id:
        rooms = rooms.filter(floor_id=floor_id)
    csv_content = export_rooms_csv(list(rooms))
    resp = HttpResponse(csv_content.encode("utf-8-sig"), content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="rooms.csv"'
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_pdf_report(request, project_id: int):
    """F8-001~004: 导出静态计算报告 PDF

    v0.5 用 reportlab 生成简化版 PDF（项目概述 + 功能区域清单）
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    project = Project.objects.get(pk=project_id)
    rooms = Room.objects.filter(floor__building__project=project)

    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    # 注册中文字体
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        font = "STSong-Light"
    except Exception:
        font = "Helvetica"

    width, height = A4
    y = height - 50
    p.setFont(font, 16)
    p.drawString(50, y, f"PCB-CoolSim 静态冷量计算报告")
    y -= 30
    p.setFont(font, 11)
    p.drawString(50, y, f"项目：{project.project_name}")
    y -= 20
    p.drawString(50, y, f"城市：{project.city.city_name if project.city else '-'}")
    y -= 30
    p.drawString(50, y, "功能区域清单：")
    y -= 20
    for room in rooms:
        if y < 60:
            p.showPage()
            p.setFont(font, 11)
            y = height - 50
        p.drawString(60, y, f"• {room.room_name}  面积={room.area}m²  体积={room.volume}m³")
        y -= 18
    p.save()
    buf.seek(0)

    resp = HttpResponse(buf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="report_{project_id}.pdf"'
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_excel_template(request):
    """附录A: 下载 Excel 导入模板"""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "功能区域"
    ws.append(["楼层名称", "功能区域名称", "面积(m²)", "吊顶高度(m)",
               "土建指标(W/m²)", "照明指标(W/m²)", "人员指标(W/人)", "人数"])
    ws.append(["1F", "示例区域", 100, 3.5, 30, 15, 60, 5])
    buf = BytesIO()
    wb.save(buf)
    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = 'attachment; filename="import_template.xlsx"'
    return resp


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_excel(request):
    """F2-032~039: Excel 批量导入"""
    f = request.FILES.get("file")
    if not f:
        return Response({"detail": "请上传文件"}, status=400)
    result = parse_excel_rooms(f.read())
    return Response(result)
