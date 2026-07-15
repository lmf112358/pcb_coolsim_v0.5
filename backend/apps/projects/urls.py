"""projects URL 路由（F2-001~026 层级 CRUD + F2-021 复制 + F3 平面图）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .floorplan_views import upload_floor_plan_pdf, floor_plan_data, available_rooms

router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet)
router.register(r"buildings", views.BuildingViewSet)
router.register(r"floors", views.FloorViewSet)
router.register(r"rooms", views.RoomViewSet)

urlpatterns = [
    # 嵌套创建端点
    path("projects/<int:project_pk>/buildings/", views.BuildingViewSet.as_view({"post": "create"}), name="building-create"),
    path("buildings/<int:building_pk>/floors/", views.FloorViewSet.as_view({"post": "create"}), name="floor-create"),
    path("floors/<int:floor_pk>/rooms/", views.RoomViewSet.as_view({"post": "create"}), name="room-create"),
    # F3 平面图
    path("floors/<int:floor_id>/floor-plan/upload/", upload_floor_plan_pdf, name="floor-plan-upload"),
    path("floors/<int:floor_id>/floor-plan/", floor_plan_data, name="floor-plan-data"),
    path("floors/<int:floor_id>/floor-plan/available-rooms/", available_rooms, name="floor-plan-available-rooms"),
    path("", include(router.urls)),
]
