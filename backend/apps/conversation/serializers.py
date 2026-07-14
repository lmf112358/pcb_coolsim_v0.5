"""对话采集序列化器（F2-046~061）"""
from rest_framework import serializers
from .models import ConversationSession, ConversationMessage


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = ["id", "session", "role", "content", "extracted_payload",
                  "stage", "timestamp"]
        read_only_fields = ["id", "session", "timestamp"]


class ConversationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationSession
        fields = ["id", "project", "current_stage", "stage_status",
                  "draft_payload", "created_at", "updated_at"]
        read_only_fields = ["id", "project", "created_at", "updated_at"]
