"""common URL 路由（F9 系统设置）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"cities", views.CityConfigViewSet)
router.register(r"water-temp-configs", views.WaterTempConfigViewSet)

urlpatterns = [
    path("projects/<int:project_pk>/water-temp-configs/",
         views.WaterTempConfigViewSet.as_view({"post": "create", "get": "list"}),
         name="water-temp-config-create"),
    path("defaults/", views.get_defaults, name="get-defaults"),
    path("", include(router.urls)),
]
