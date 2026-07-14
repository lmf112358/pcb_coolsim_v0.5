"""projects CRUD API 测试（F2-001~013 层级管理 + F2-021 复制 + ADR-0007 对话表）"""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.projects.models import Project, Building, Floor, Room
from apps.conversation.models import ConversationSession, ConversationMessage


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="puser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestProjectAPI:
    """F1-015~023: 项目 CRUD"""

    def test_list_projects(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get("/api/v1/projects/")
        assert resp.status_code == 200
        assert len(resp.data["results"]) >= 1

    def test_create_project(self, db, city_guangzhou, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post("/api/v1/projects/", {
            "project_name": "新工厂", "city": city_guangzhou.id,
        }, format="json")
        assert resp.status_code == 201
        assert Project.objects.filter(project_name="新工厂").exists()

    def test_project_detail(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/projects/{project.id}/")
        assert resp.status_code == 200
        assert resp.data["project_name"] == project.project_name

    def test_delete_project(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.delete(f"/api/v1/projects/{project.id}/")
        assert resp.status_code == 204
        assert not Project.objects.filter(id=project.id).exists()


class TestBuildingAPI:
    """F2-009~011: 建筑 CRUD"""

    def test_create_building(self, db, project, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/projects/{project.id}/buildings/", {
            "building_name": "2#厂房",
        }, format="json")
        assert resp.status_code == 201
        assert Building.objects.filter(project=project, building_name="2#厂房").exists()


class TestFloorAPI:
    """F2-012~013: 楼层 CRUD"""

    def test_create_floor(self, db, building, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/buildings/{building.id}/floors/", {
            "floor_name": "2F",
        }, format="json")
        assert resp.status_code == 201


class TestRoomAPI:
    """F2-014~020: 功能区域 CRUD + F2-021 复制"""

    def test_create_room(self, db, floor, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/floors/{floor.id}/rooms/", {
            "room_name": "曝光区", "area": "120", "height": "3.5",
            "civil_load_index": "30", "lighting_load_index": "15",
        }, format="json")
        assert resp.status_code == 201
        assert Room.objects.filter(room_name="曝光区").exists()

    def test_room_volume_auto_in_response(self, db, room_standard, engineer_role):
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/rooms/{room_standard.id}/")
        assert resp.status_code == 200
        # volume 自动计算
        assert Decimal(resp.data["volume"]) == Decimal("350.00")

    def test_copy_room(self, db, room_standard, engineer_role):
        """F2-021: 复制功能区域"""
        c = auth_client(db, engineer_role)
        resp = c.post(f"/api/v1/rooms/{room_standard.id}/copy/", {
            "room_name": "电镀区-副本",
        }, format="json")
        assert resp.status_code == 201
        assert Room.objects.filter(room_name="电镀区-副本").exists()
        # 原始仍在
        assert Room.objects.filter(id=room_standard.id).exists()


class TestConversationModel:
    """ADR-0007: 对话采集会话与消息"""

    def test_create_session(self, db, project):
        session = ConversationSession.objects.create(project=project)
        assert session.current_stage == "s1_project"
        assert session.stage_status == {}

    def test_session_resume(self, db, project):
        """F2-057: 断点续采——更新 current_stage"""
        session = ConversationSession.objects.create(project=project, current_stage="s3_building")
        assert session.current_stage == "s3_building"

    def test_message_history(self, db, project):
        """F2-051: 消息历史回看"""
        session = ConversationSession.objects.create(project=project)
        m1 = ConversationMessage.objects.create(
            session=session, role="system", content="请配置冷冻水", stage="s2_water_temp"
        )
        m2 = ConversationMessage.objects.create(
            session=session, role="user", content="低温7/12", stage="s2_water_temp"
        )
        msgs = session.messages.all()
        assert msgs.count() == 2
        assert msgs.first().role == "system"
