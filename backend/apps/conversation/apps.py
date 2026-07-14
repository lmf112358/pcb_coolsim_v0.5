"""对话式采集应用配置"""
from django.apps import AppConfig


class ConversationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.conversation"
    verbose_name = "对话式采集"
