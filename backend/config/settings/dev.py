"""开发环境配置（CI/本地开发）"""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# CORS 开发环境全开
CORS_ALLOW_ALL_ORIGINS = True

# 调试工具
INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]  # noqa: F405
MIDDLEWARE = MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405

# 测试数据库（CI 用 coolsim_test）
if os.environ.get("DB_NAME"):  # noqa: F405
    DATABASES["default"]["NAME"] = os.environ["DB_NAME"]  # noqa: F405
