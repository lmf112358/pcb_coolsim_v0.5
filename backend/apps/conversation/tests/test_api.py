"""对话采集 API 测试（F2-046~061，六阶段会话/消息）"""
import pytest
from rest_framework.test import APIClient


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="convuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestConversationSessionAPI:
    """F2-046~061 对话式采集"""

    def test_create_session(self, db, project, engineer_role):
        """F2-046: 创建会话"""
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        assert resp.status_code == 201
        assert "id" in resp.data
        assert resp.data["current_stage"] == "s1_project"

    def test_get_session(self, db, project, engineer_role):
        """F2-047: 获取会话状态"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        resp = c.get(f"/api/v1/conversation-sessions/{sid}/")
        assert resp.status_code == 200

    def test_advance_stage(self, db, project, engineer_role):
        """F2-048: 阶段推进（s1→s2）"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        resp = c.patch(f"/api/v1/conversation-sessions/{sid}/", {
            "current_stage": "s2_water_temp",
        }, format="json")
        assert resp.status_code == 200
        assert resp.data["current_stage"] == "s2_water_temp"

    def test_send_message(self, db, project, engineer_role):
        """F2-049/050: 发送消息"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        resp = c.post(f"/api/v1/conversation-sessions/{sid}/messages/", {
            "role": "user",
            "content": "配置低温7/12度",
            "stage": "s2_water_temp",
        }, format="json")
        assert resp.status_code == 201

    def test_list_messages(self, db, project, engineer_role):
        """F2-051: 消息历史回看"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        c.post(f"/api/v1/conversation-sessions/{sid}/messages/", {
            "role": "user", "content": "msg1", "stage": "s1_project",
        }, format="json")
        c.post(f"/api/v1/conversation-sessions/{sid}/messages/", {
            "role": "system", "content": "msg2", "stage": "s1_project",
        }, format="json")
        resp = c.get(f"/api/v1/conversation-sessions/{sid}/messages/")
        assert resp.status_code == 200
        assert len(resp.data["results"]) == 2

    def test_save_draft(self, db, project, engineer_role):
        """F2-058: 保存草稿（断点续采）"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        resp = c.patch(f"/api/v1/conversation-sessions/{sid}/", {
            "draft_payload": {"city": "广州"},
        }, format="json")
        assert resp.status_code == 200

    def test_finalize(self, db, project, engineer_role):
        """F2-059: 汇总确认（finalize）"""
        c = auth_client(db, engineer_role)
        create = c.post(f"/api/v1/projects/{project.id}/conversation-sessions/", {}, format="json")
        sid = create.data["id"]
        resp = c.post(f"/api/v1/conversation-sessions/{sid}/finalize/", {}, format="json")
        assert resp.status_code == 200
        assert resp.data["current_stage"] == "s6_summary"
