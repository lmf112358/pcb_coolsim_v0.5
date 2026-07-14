"""负荷预测应用配置"""
from django.apps import AppConfig


class ForecastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.forecast"
    verbose_name = "负荷预测"
