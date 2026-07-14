"""动态仿真模型（F6-020~023）

SimulationRun：仿真任务批次（mode/status/进度/结果摘要）
"""
import uuid

from django.db import models


class SimulationRun(models.Model):
    """仿真任务（F6-020~023）"""

    MODE_CHOICES = [
        ("weather_driven", "气象驱动"),
        ("ratio_coefficient", "比例系数法"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "等待"),
        ("STARTED", "进行中"),
        ("SUCCESS", "成功"),
        ("FAILURE", "失败"),
    ]

    batch_id = models.UUIDField("批次ID", default=uuid.uuid4, editable=False, unique=True)
    room = models.ForeignKey(
        "projects.Room", on_delete=models.CASCADE, related_name="simulation_runs",
        verbose_name="功能区域",
    )
    mode = models.CharField("仿真模式", max_length=20, default="weather_driven", choices=MODE_CHOICES)
    status = models.CharField("状态", max_length=10, default="SUCCESS", choices=STATUS_CHOICES)
    result_summary = models.JSONField("结果摘要", default=dict, blank=True)
    error_message = models.TextField("错误信息", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "SimulationRun"
        verbose_name = "仿真任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.room.room_name} {self.batch_id}"
