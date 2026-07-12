"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


class TestAuthRegister:
    """Tests for POST /api/v1/auth/register"""
    
    @pytest.mark.unit
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert "message" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["first_name"] == "New"
        assert data["user"]["last_name"] == "User"
        assert "id" in data["user"]
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
    
    @pytest.mark.unit
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "SecurePassword123!",
                "first_name": "Duplicate",
                "last_name": "User",
            },
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"].lower()
    
    @pytest.mark.unit
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",
                "first_name": "Weak",
                "last_name": "User",
            },
        )
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePassword123!",
                "first_name": "Invalid",
                "last_name": "User",
            },
        )
        assert response.status_code == 422


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login"""
    
    @pytest.mark.unit
    def test_login_success(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"
    
    @pytest.mark.unit
    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["message"].lower()
    
    @pytest.mark.unit
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!",
            },
        )
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_login_inactive_user(self, client: TestClient, db: Session):
        """Test login with inactive user fails."""
        from tests.conftest import create_test_user
        
        user = create_test_user(db, email="inactive@example.com", is_active=False)
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "Password123!",
            },
        )
        assert response.status_code == 401


class TestAuthRefresh:
    """Tests for POST /api/v1/auth/refresh"""
    
    @pytest.mark.unit
    def test_refresh_token_success(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        refresh_token = login_response.json()["token"]["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.unit
    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token fails."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401


class TestAuthMe:
    """Tests for GET /api/v1/auth/me"""
    
    @pytest.mark.unit
    def test_get_current_user(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
    
    @pytest.mark.unit
    def test_get_current_user_no_auth(self, client: TestClient):
        """Test getting current user without auth fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


class TestAuthLogout:
    """Tests for POST /api/v1/auth/logout"""
    
    @pytest.mark.unit
    def test_logout_success(self, client: TestClient, test_user: User, test_user_data: dict, auth_headers: dict):
        """Test successful logout."""
        # First login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        refresh_token = login_response.json()["token"]["refresh_token"]
        
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_logout_no_auth(self, client: TestClient):
        """Test logout without auth fails."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401


class TestPasswordReset:
    """Tests for password reset flow"""
    
    @pytest.mark.unit
    def test_forgot_password_success(self, client: TestClient, test_user: User):
        """Test forgot password request."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email},
        )
        # Should return 200 even if email doesn't exist (security)
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Test forgot password with non-existent email still succeeds (security)."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )
        # Should still return 200 to prevent email enumeration
        assert response.status_code == 200


class TestChangePassword:
    """Tests for POST /api/v1/auth/change-password"""
    
    @pytest.mark.unit
    def test_change_password_success(
        self, client: TestClient, test_user: User, test_user_data: dict, auth_headers: dict
    ):
        """Test successful password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewSecurePassword123!",
            },
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: dict):
        """Test password change with wrong current password fails."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewSecurePassword123!",
            },
        )
        assert response.status_code == 400
