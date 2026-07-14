"""静态冷量计算应用配置"""
from django.apps import AppConfig


class CalculationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.calculation"
    verbose_name = "静态冷量计算"
