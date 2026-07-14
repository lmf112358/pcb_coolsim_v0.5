"""账户与权限模型（模块一，F1-001~029）

对齐数据库设计 PascalCase 表名约定：
- User（账户，bcrypt 加密 NF-020）
- Role（角色，四角色 RBAC F1-024）

注意：表名 PascalCase（ORM 模型类名），字段 snake_case（Python/DB 字段层）。
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """角色（F1-024，四种系统角色）"""

    name = models.CharField("角色名", max_length=50, unique=True)
    permissions = models.JSONField("权限矩阵", default=dict, blank=True)
    description = models.CharField("角色描述", max_length=200, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "Role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """用户（F1-001，自定义用户模型，bcrypt 加密）"""

    # 四角色（管理员 admin / 项目经理 pm / 工程师 engineer / 查看者 viewer）
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users",
        verbose_name="角色", null=True, blank=True,
    )
    email = models.EmailField("邮箱", blank=True)
    is_active = models.BooleanField("是否启用", default=True)
    last_login = models.DateTimeField("最近登录", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    # 移除 AbstractUser 的 first_name/last_name（本项目不用）
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    class Meta:
        db_table = "User"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.username
