"""PCB-CoolSim URL 路由

API 路径统一 /api/v1/ 前缀（命名基线，CLAUDE.md）
端点对应 PRD 附录 D 与 03-接口级-Spec/ 各接口文档
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # 认证（F1-001~006）
    path("api/v1/auth/login/", TokenObtainPairView.as_view(), name="token_login"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 业务模块（各 app 的 urls.py 逐步实现）
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.projects.urls")),
    path("api/v1/", include("apps.calculation.urls")),
    path("api/v1/", include("apps.simulation.urls")),
    path("api/v1/", include("apps.forecast.urls")),
    path("api/v1/", include("apps.conversation.urls")),
    path("api/v1/", include("apps.exports.urls")),
    path("api/v1/", include("apps.common.urls")),
]
