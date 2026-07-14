"""conversation URL 路由（F2-046~061）"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"conversation-sessions", views.ConversationSessionViewSet)

urlpatterns = [
    path("projects/<int:project_pk>/conversation-sessions/",
         views.ConversationSessionViewSet.as_view({"post": "create", "get": "list"}),
         name="conversation-session-create"),
    path("", include(router.urls)),
]
