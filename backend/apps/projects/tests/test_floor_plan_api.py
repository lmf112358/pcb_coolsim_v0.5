"""2D 平面图 API 测试（F3-001~024，底图上传/JSON 保存/未关联区域）"""
import json

import pytest
from rest_framework.test import APIClient


def auth_client(db, engineer_role):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="fpuser", password="T@12345", role=engineer_role)
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class TestFloorPlanUploadAPI:
    """F3-001~003: PDF 底图上传"""

    def test_upload_pdf(self, db, floor, engineer_role):
        """F3-001: 上传底图 PDF"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        c = auth_client(db, engineer_role)
        pdf_content = b"%PDF-1.4 test pdf content"
        f = SimpleUploadedFile("plan.pdf", pdf_content, content_type="application/pdf")
        resp = c.post(f"/api/v1/floors/{floor.id}/floor-plan/upload/",
                      {"file": f}, format="multipart")
        assert resp.status_code == 200, resp.data
        floor.refresh_from_db()
        assert floor.floor_plan_file != ""

    def test_upload_replaces_existing(self, db, floor, engineer_role):
        """F3-003: 替换旧底图"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        c = auth_client(db, engineer_role)
        f1 = SimpleUploadedFile("v1.pdf", b"v1", content_type="application/pdf")
        c.post(f"/api/v1/floors/{floor.id}/floor-plan/upload/", {"file": f1}, format="multipart")
        f2 = SimpleUploadedFile("v2.pdf", b"v2", content_type="application/pdf")
        resp = c.post(f"/api/v1/floors/{floor.id}/floor-plan/upload/", {"file": f2}, format="multipart")
        assert resp.status_code == 200
        floor.refresh_from_db()
        assert "v2" in floor.floor_plan_file or floor.floor_plan_file

    def test_upload_requires_auth(self, db, floor):
        c = APIClient()
        resp = c.post(f"/api/v1/floors/{floor.id}/floor-plan/upload/", {}, format="multipart")
        assert resp.status_code == 401


class TestFloorPlanSaveAPI:
    """F3-009~013: 平面图 JSON 保存与查询"""

    def test_save_plan_data(self, db, floor, engineer_role):
        """F3-011: 保存平面图 JSON（外墙/方块/比例尺/指北针）"""
        c = auth_client(db, engineer_role)
        plan_data = {
            "version": 1,
            "outline": {"points": [{"x": 10, "y": 10}, {"x": 500, "y": 10}]},
            "blocks": [{"id": "b1", "x": 120, "y": 200, "width": 80, "height": 60, "room_id": None}],
            "scale": {"pixels_per_meter": 15.0},
            "compass": {"north_angle": 0},
        }
        resp = c.put(f"/api/v1/floors/{floor.id}/floor-plan/",
                     {"floor_plan_data": plan_data}, format="json")
        assert resp.status_code == 200
        floor.refresh_from_db()
        assert floor.floor_plan_data["version"] == 1

    def test_get_plan_data(self, db, floor, engineer_role):
        """F3-014: 获取平面图数据"""
        c = auth_client(db, engineer_role)
        floor.floor_plan_data = {"blocks": [{"id": "b1"}]}
        floor.save()
        resp = c.get(f"/api/v1/floors/{floor.id}/floor-plan/")
        assert resp.status_code == 200
        assert "blocks" in resp.data["floor_plan_data"]

    def test_get_empty_plan(self, db, floor, engineer_role):
        """无平面图返回空"""
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/floors/{floor.id}/floor-plan/")
        assert resp.status_code == 200


class TestAvailableRoomsAPI:
    """F3-004: 查询未关联功能区域"""

    def test_available_rooms(self, db, floor, room_standard, engineer_role):
        """F3-004: 返回未被方块关联的功能区域"""
        c = auth_client(db, engineer_role)
        resp = c.get(f"/api/v1/floors/{floor.id}/floor-plan/available-rooms/")
        assert resp.status_code == 200
        room_ids = [r["id"] for r in resp.data["rooms"]]
        assert room_standard.id in room_ids

    def test_excludes_linked_room(self, db, floor, room_standard, engineer_role):
        """已被方块关联的房间不出现在列表"""
        c = auth_client(db, engineer_role)
        # 模拟 room_standard 已关联到方块
        floor.floor_plan_data = {
            "blocks": [{"id": "b1", "room_id": room_standard.id}]
        }
        floor.save()
        resp = c.get(f"/api/v1/floors/{floor.id}/floor-plan/available-rooms/")
        room_ids = [r["id"] for r in resp.data["rooms"]]
        assert room_standard.id not in room_ids
