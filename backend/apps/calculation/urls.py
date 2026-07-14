"""静态冷量计算 URL 路由（F4-001）"""
from django.urls import path
from . import views

app_name = "calculation"

urlpatterns = [
    path("calc/static/<int:room_id>/", views.calc_static_view, name="calc-static"),
]
