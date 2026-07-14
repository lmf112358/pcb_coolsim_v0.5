"""测试环境配置（SQLite，无外部依赖）"""
from .base import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
# 测试不连 Redis/PG，关闭 Celery eager
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
# 密码哈希用明文加速测试
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
