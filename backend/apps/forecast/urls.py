"""forecast URL 路由（F10-001~021）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"forecast-scenarios", views.ForecastScenarioViewSet)

urlpatterns = [
    path("projects/<int:project_pk>/forecast-scenarios/",
         views.ForecastScenarioViewSet.as_view({"post": "create", "get": "list"}),
         name="forecast-scenario-create"),
    path("", include(router.urls)),
]
