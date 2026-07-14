"""对话采集 API 视图（F2-046~061，六阶段 SOP）"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import Project
from .models import ConversationSession, ConversationMessage
from .serializers import ConversationSessionSerializer, ConversationMessageSerializer


class ConversationSessionViewSet(viewsets.ModelViewSet):
    """对话采集会话（F2-046~061）"""
    queryset = ConversationSession.objects.all()
    serializer_class = ConversationSessionSerializer

    def create(self, request, project_pk=None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        """GET/POST /conversation-sessions/{id}/messages/ 消息历史与发送（F2-049/051）"""
        session = get_object_or_404(ConversationSession, pk=pk)
        if request.method == "POST":
            serializer = ConversationMessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # GET：消息历史
        msgs = session.messages.all()
        page = self.paginate_queryset(msgs)
        if page is not None:
            serializer = ConversationMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ConversationMessageSerializer(msgs, many=True)
        return Response({"results": serializer.data})

    @action(detail=True, methods=["post"], url_path="finalize")
    def finalize(self, request, pk=None):
        """POST /conversation-sessions/{id}/finalize/ 汇总确认（F2-059）"""
        session = get_object_or_404(ConversationSession, pk=pk)
        session.current_stage = "s6_summary"
        session.save()
        return Response(ConversationSessionSerializer(session).data)

    def get_queryset(self):
        qs = ConversationSession.objects.all()
        project_id = self.kwargs.get("project_pk") or self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs
