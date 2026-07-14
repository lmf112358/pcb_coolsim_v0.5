"""Celery 配置（ADR-0002，异步任务与定时调度）

- worker：气象拉取 / 仿真计算 / 报告生成 / Excel 导入
- beat：每小时天气预报更新（PRD G11 / F10-006）
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("coolsim")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
