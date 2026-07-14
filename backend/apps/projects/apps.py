"""项目/建筑/楼层/功能区域应用配置"""
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "项目/建筑/楼层/功能区域"
