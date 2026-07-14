"""exports URL 路由（F8-001~014）"""
from django.urls import path
from . import views

app_name = "exports"

urlpatterns = [
    path("exports/rooms-csv/", views.export_rooms_csv_view, name="export-rooms-csv"),
    path("exports/pdf-report/<int:project_id>/", views.export_pdf_report, name="export-pdf"),
    path("exports/excel-template/", views.download_excel_template, name="excel-template"),
    path("exports/import-excel/", views.import_excel, name="import-excel"),
]
