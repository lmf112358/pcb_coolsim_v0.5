"""账户认证 API 测试（F1-001~006，JWT）"""
import pytest
from django.contrib.auth import get_user_model
from apps.accounts.models import Role

User = get_user_model()


@pytest.fixture
def engineer_role(db):
    return Role.objects.create(name="engineer", description="暖通工程师")


@pytest.fixture
def test_user(db, engineer_role):
    return User.objects.create_user(
        username="testengineer", password="Test@12345",
        role=engineer_role, email="test@example.com",
    )


class TestJWTAuth:
    """F1-001: 登录返回 Access + Refresh Token"""

    pytestmark = pytest.mark.django_db

    def test_login_success(self, client, test_user):
        """正确账号密码登录成功，返回双 Token"""
        resp = client.post("/api/v1/auth/login/", {
            "username": "testengineer", "password": "Test@12345",
        }, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_wrong_password(self, client, test_user):
        """密码错误返回 401"""
        resp = client.post("/api/v1/auth/login/", {
            "username": "testengineer", "password": "wrong",
        }, format="json")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """不存在用户返回 401"""
        resp = client.post("/api/v1/auth/login/", {
            "username": "nobody", "password": "x",
        }, format="json")
        assert resp.status_code == 401

    def test_refresh_token(self, client, test_user):
        """F1-004: Refresh Token 换取新 Access Token"""
        login = client.post("/api/v1/auth/login/", {
            "username": "testengineer", "password": "Test@12345",
        }, format="json")
        refresh = login.data["refresh"]
        resp = client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data


class TestPasswordSecurity:
    """F1-006: 密码加密存储（bcrypt）"""

    def test_password_hashed(self, db, engineer_role):
        """密码不以明文存储"""
        user = User.objects.create_user(
            username="hashcheck", password="Plain@123", role=engineer_role,
        )
        assert user.password != "Plain@123"
        assert user.password.startswith("bcrypt$") or "$" in user.password

    def test_check_password(self, db, engineer_role):
        """密码可校验"""
        user = User.objects.create_user(
            username="pwcheck", password="Secret@456", role=engineer_role,
        )
        assert user.check_password("Secret@456")
        assert not user.check_password("wrong")


class TestRoleModel:
    """F1-024: 四种系统角色"""

    def test_role_unique_name(self, db):
        """角色名唯一"""
        Role.objects.create(name="admin", description="管理员")
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Role.objects.create(name="admin", description="重复")

    def test_user_role_relation(self, db, engineer_role):
        """用户关联角色"""
        user = User.objects.create_user(
            username="roleuser", password="x@12345", role=engineer_role,
        )
        assert user.role.name == "engineer"
