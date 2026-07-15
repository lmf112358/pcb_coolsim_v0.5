"""common URL 路由（F9 系统设置 + F4-043~050 气象数据管理）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"cities", views.CityConfigViewSet)
router.register(r"water-temp-configs", views.WaterTempConfigViewSet)

urlpatterns = [
    # F9 冷冻水配置
    path("projects/<int:project_pk>/water-temp-configs/",
         views.WaterTempConfigViewSet.as_view({"post": "create", "get": "list"}),
         name="water-temp-config-create"),
    # F9 默认值
    path("defaults/", views.get_defaults, name="get-defaults"),
    # F4-043~050 气象数据管理
    path("weather/<int:city_id>/summary/", views.weather_summary, name="weather-summary"),
    path("weather/<int:city_id>/upload/", views.weather_upload, name="weather-upload"),
    path("weather/<int:city_id>/quality/", views.weather_quality, name="weather-quality"),
    path("weather/fetch/<int:city_id>/", views.weather_fetch, name="weather-fetch"),
    path("", include(router.urls)),
]
