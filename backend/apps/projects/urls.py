"""projects URL 路由（F2-001~026 层级 CRUD + F2-021 复制）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
    path("", include(router.urls)),
]
