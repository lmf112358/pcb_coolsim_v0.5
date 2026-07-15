"""开发环境配置（CI/本地开发）"""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# CORS 开发环境全开
CORS_ALLOW_ALL_ORIGINS = True

# 调试工具
INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]  # noqa: F405
MIDDLEWARE = MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405

# 使用SQLite快速启动（开发环境）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# 简化配置，不使用TimescaleDB扩展
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "timescaledb"]  # noqa: F405

# 不使用Celery（开发环境简化）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试数据库（CI 用 coolsim_test）
if os.environ.get("DB_NAME"):  # noqa: F405
    DATABASES["default"]["NAME"] = os.environ["DB_NAME"]  # noqa: F405
