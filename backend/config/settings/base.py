"""
PCB-CoolSim 后端基础配置
技术栈对齐 PRD v0.5.1 / CLAUDE.md：Django 5 + DRF + Celery 5 + PG16/TimescaleDB + Redis 7
"""
import os
from datetime import timedelta
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 从 .env 读取（python-dotenv）
from dotenv import load_dotenv
load_dotenv(BASE_DIR.parent / ".env")

# 安全
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-in-production")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

# 应用（apps 按 PRD 模块组织，PascalCase 表名见各 models.py）
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "timescaledb",
]
LOCAL_APPS = [
    "apps.accounts",        # 模块一：账户与项目管理（User/Role/JWT）
    "apps.projects",        # 模块一/二：项目/建筑/楼层/功能区域
    "apps.calculation",     # 模块四：静态冷量计算（核心，PRD §15）
    "apps.simulation",      # 模块六/七：动态仿真/8760 可视化
    "apps.forecast",        # 模块十：负荷预测
    "apps.conversation",    # 模块二：对话式采集（ADR-0007）
    "apps.exports",         # 模块八：报告与数据导出
    "apps.common",          # 公共：城市配置/冷冻水配置/默认值/模板/日志
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# 模板
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 数据库（PostgreSQL 16 + TimescaleDB，PRD NF-030）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "coolsim"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 自定义用户模型（模块一 F1-001，bcrypt 加密 NF-020）
AUTH_USER_MODEL = "accounts.User"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.BCryptSHA256PasswordHasher"]

# 国际化（项目要求全中文界面，但后端保持 en-us 代码层）
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# 默认主键（BIGINT，对齐数据库设计）
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # 测试 force_authenticate 用
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

# JWT（F1-001/F1-004，Access + Refresh）
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Celery（ADR-0002，Redis broker + result backend）
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# MinIO/S3 文件存储（PRD NF，底图 PDF/导出文件）
AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
AWS_STORAGE_ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
AWS_S3_SIGNATURE_VERSION = "s3v4"

# 文件上传（NF-025，PDF/Excel，≤50MB）
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
