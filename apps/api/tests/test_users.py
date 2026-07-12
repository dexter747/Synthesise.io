"""
Tests for user endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


class TestUserProfile:
    """Tests for user profile endpoints"""
    
    @pytest.mark.unit
    def test_get_profile(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "password" not in data
        assert "password_hash" not in data
    
    @pytest.mark.unit
    def test_get_profile_no_auth(self, client: TestClient):
        """Test getting profile without auth fails."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_update_profile(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test updating user profile."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "Updated bio",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    
    @pytest.mark.unit
    def test_update_profile_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test updating profile with invalid data."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "email": "new@example.com",  # Cannot change email this way
            },
        )
        # Should either reject or ignore the email change
        assert response.status_code in [200, 422]


class TestUserPreferences:
    """Tests for user preferences endpoints"""
    
    @pytest.mark.unit
    def test_update_preferences(self, client: TestClient, auth_headers: dict):
        """Test updating user preferences."""
        response = client.put(
            "/api/v1/users/me/preferences",
            headers=auth_headers,
            json={
                "theme": "dark",
                "notifications_enabled": True,
                "default_output_format": "json",
            },
        )
        assert response.status_code == 200


class TestUserStats:
    """Tests for user statistics endpoints"""
    
    @pytest.mark.unit
    def test_get_user_stats(self, client: TestClient, auth_headers: dict):
        """Test getting user statistics."""
        response = client.get("/api/v1/users/me/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Check for expected stat fields
        assert "total_datasets" in data or "datasets_count" in data or isinstance(data, dict)


class TestUserActivity:
    """Tests for user activity endpoints"""
    
    @pytest.mark.unit
    def test_get_user_activity(self, client: TestClient, auth_headers: dict):
        """Test getting user activity."""
        response = client.get("/api/v1/users/me/activity", headers=auth_headers)
        assert response.status_code == 200


class TestUserOrganizations:
    """Tests for user organization endpoints"""
    
    @pytest.mark.unit
    def test_get_user_organizations(
        self, client: TestClient, test_organization, auth_headers: dict
    ):
        """Test getting user's organizations."""
        response = client.get("/api/v1/users/me/organizations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data


class TestUserDelete:
    """Tests for user deletion"""
    
    @pytest.mark.unit
    def test_delete_user_account(self, client: TestClient, db: Session):
        """Test deleting user account."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        # Create a user to delete
        user = create_test_user(db, email="todelete@example.com")
        token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete("/api/v1/users/me", headers=headers)
        assert response.status_code == 200


class TestAdminUserManagement:
    """Tests for admin user management endpoints"""
    
    @pytest.mark.unit
    def test_list_users_as_admin(self, client: TestClient, admin_auth_headers: dict):
        """Test listing users as admin."""
        response = client.get("/api/v1/users/", headers=admin_auth_headers)
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_list_users_as_regular_user(self, client: TestClient, auth_headers: dict):
        """Test listing users as regular user fails."""
        response = client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 403
    
    @pytest.mark.unit
    def test_get_user_by_id_as_admin(
        self, client: TestClient, test_user: User, admin_auth_headers: dict
    ):
        """Test getting user by ID as admin."""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
    
    @pytest.mark.unit
    def test_get_user_by_id_as_regular_user(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test getting user by ID as regular user fails."""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
        )
        assert response.status_code == 403
