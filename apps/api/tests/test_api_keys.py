"""
Tests for API key endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, APIKey


class TestAPIKeyCRUD:
    """Tests for API key CRUD operations"""
    
    @pytest.mark.unit
    def test_create_api_key(self, client: TestClient, auth_headers: dict):
        """Test creating a new API key."""
        response = client.post(
            "/api/v1/api-keys/",
            headers=auth_headers,
            json={
                "name": "Test API Key",
                "scopes": ["datasets:read", "jobs:read"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test API Key"
        assert "key" in data  # The raw key should be returned on creation
        assert "id" in data
    
    @pytest.mark.unit
    def test_create_api_key_no_auth(self, client: TestClient):
        """Test creating API key without auth fails."""
        response = client.post(
            "/api/v1/api-keys/",
            json={"name": "Unauthorized Key"},
        )
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_list_api_keys(
        self, client: TestClient, test_api_key: tuple[APIKey, str], auth_headers: dict
    ):
        """Test listing user's API keys."""
        response = client.get("/api/v1/api-keys/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_get_api_key(
        self, client: TestClient, test_api_key: tuple[APIKey, str], auth_headers: dict
    ):
        """Test getting a specific API key."""
        api_key, _ = test_api_key
        response = client.get(
            f"/api/v1/api-keys/{api_key.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == api_key.name
        # Should not return the full key
        assert "key" not in data or data.get("key") is None
    
    @pytest.mark.unit
    def test_get_api_key_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent API key returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/api-keys/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_update_api_key(
        self, client: TestClient, test_api_key: tuple[APIKey, str], auth_headers: dict
    ):
        """Test updating an API key."""
        api_key, _ = test_api_key
        response = client.put(
            f"/api/v1/api-keys/{api_key.id}",
            headers=auth_headers,
            json={
                "name": "Updated Key Name",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Key Name"
    
    @pytest.mark.unit
    def test_delete_api_key(
        self, client: TestClient, db: Session, test_user: User, auth_headers: dict
    ):
        """Test deleting an API key."""
        import uuid
        from datetime import datetime
        from app.core.security import hash_password
        
        api_key = APIKey(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="To Delete Key",
            key_prefix="todelete",
            key_hash=hash_password("test-key"),
            scopes=["datasets:read"],
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(api_key)
        db.commit()
        
        response = client.delete(
            f"/api/v1/api-keys/{api_key.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestAPIKeyOperations:
    """Tests for API key operations"""
    
    @pytest.mark.unit
    def test_revoke_all_keys(self, client: TestClient, auth_headers: dict):
        """Test revoking all API keys."""
        response = client.post(
            "/api/v1/api-keys/revoke-all",
            headers=auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_rotate_api_key(
        self, client: TestClient, test_api_key: tuple[APIKey, str], auth_headers: dict
    ):
        """Test rotating an API key."""
        api_key, _ = test_api_key
        response = client.post(
            f"/api/v1/api-keys/{api_key.id}/rotate",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Should return new key
        assert "key" in data


class TestAPIKeyUsage:
    """Tests for API key usage tracking"""
    
    @pytest.mark.unit
    def test_get_key_usage(
        self, client: TestClient, test_api_key: tuple[APIKey, str], auth_headers: dict
    ):
        """Test getting API key usage."""
        api_key, _ = test_api_key
        response = client.get(
            f"/api/v1/api-keys/{api_key.id}/usage",
            headers=auth_headers,
        )
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.unit
    def test_get_usage_summary(self, client: TestClient, auth_headers: dict):
        """Test getting usage summary."""
        response = client.get(
            "/api/v1/api-keys/usage/summary",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestAPIKeyScopes:
    """Tests for API key scopes"""
    
    @pytest.mark.unit
    def test_list_available_scopes(self, client: TestClient, auth_headers: dict):
        """Test listing available scopes."""
        response = client.get("/api/v1/api-keys/scopes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "scopes" in data


class TestAPIKeyAuthentication:
    """Tests for API key authentication"""
    
    @pytest.mark.unit
    def test_authenticate_with_api_key(
        self, client: TestClient, api_key_headers: dict
    ):
        """Test authenticating with API key."""
        response = client.get("/api/v1/datasets/", headers=api_key_headers)
        # Should work if the key has datasets:read scope
        assert response.status_code in [200, 403]  # 403 if scope check fails
    
    @pytest.mark.unit
    def test_invalid_api_key(self, client: TestClient):
        """Test authentication with invalid API key fails."""
        response = client.get(
            "/api/v1/datasets/",
            headers={"X-API-Key": "invalid-key"},
        )
        assert response.status_code == 401


class TestAPIKeyPermissions:
    """Tests for API key permission checks"""
    
    @pytest.mark.unit
    def test_cannot_access_other_user_key(
        self, client: TestClient, db: Session, test_api_key: tuple[APIKey, str]
    ):
        """Test that users cannot access other users' API keys."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        api_key, _ = test_api_key
        
        other_user = create_test_user(db, email="keyother@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/v1/api-keys/{api_key.id}",
            headers=headers,
        )
        assert response.status_code in [403, 404]
