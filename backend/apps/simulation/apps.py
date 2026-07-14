"""动态仿真/8760可视化应用配置"""
from django.apps import AppConfig


class SimulationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.simulation"
    verbose_name = "动态仿真/8760可视化"
