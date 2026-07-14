"""对话式采集模型（模块二 §6.10，ADR-0007）

ConversationSession + ConversationMessage 两表：
支撑断点续采（F2-057）与对话历史回看（F2-051/F2-058）
"""
from django.db import models

# 六阶段（PRD §6.10.2）
STAGE_CHOICES = [
    ("s1_project", "①项目基本信息"),
    ("s2_water_temp", "②冷冻水温度配置"),
    ("s3_building", "③建筑结构信息"),
    ("s4_room", "④功能区域参数"),
    ("s5_extra_load", "⑤额外负荷信息"),
    ("s6_summary", "⑥汇总预览与确认"),
]

ROLE_CHOICES = [
    ("system", "系统"),
    ("user", "用户"),
    ("assistant", "助手"),
]


class ConversationSession(models.Model):
    """对话采集会话（F2-057 断点续采）"""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="conversation_sessions",
        verbose_name="所属项目",
    )
    current_stage = models.CharField(
        "当前阶段", max_length=20, default="s1_project", choices=STAGE_CHOICES,
    )
    stage_status = models.JSONField("各阶段完成状态", default=dict, blank=True)
    draft_payload = models.JSONField("对话草稿暂存", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "ConversationSession"
        verbose_name = "对话采集会话"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.project.project_name} 会话 @ {self.current_stage}"


class ConversationMessage(models.Model):
    """对话消息历史（F2-051/F2-058 历史回看）"""

    session = models.ForeignKey(
        ConversationSession, on_delete=models.CASCADE, related_name="messages",
        verbose_name="所属会话",
    )
    role = models.CharField("角色", max_length=10, choices=ROLE_CHOICES)
    content = models.TextField("消息内容")
    extracted_payload = models.JSONField("抽取结果", default=dict, blank=True)
    stage = models.CharField("所属阶段", max_length=20, choices=STAGE_CHOICES)
    timestamp = models.DateTimeField("时间戳", auto_now_add=True)

    class Meta:
        db_table = "ConversationMessage"
        verbose_name = "对话消息"
        verbose_name_plural = verbose_name
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"{self.session_id} [{self.role}] {self.content[:30]}"
