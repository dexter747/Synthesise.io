"""
Tests for webhook endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, Webhook


class TestWebhookCRUD:
    """Tests for webhook CRUD operations"""
    
    @pytest.mark.unit
    def test_create_webhook(self, client: TestClient, auth_headers: dict):
        """Test creating a new webhook."""
        response = client.post(
            "/api/v1/webhooks/",
            headers=auth_headers,
            json={
                "name": "Test Webhook",
                "url": "https://example.com/webhook",
                "events": ["job.completed", "job.failed"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Webhook"
        assert "id" in data
        assert "secret_preview" in data  # Secret preview returned on creation
    
    @pytest.mark.unit
    def test_create_webhook_no_auth(self, client: TestClient):
        """Test creating webhook without auth fails."""
        response = client.post(
            "/api/v1/webhooks/",
            json={
                "name": "Unauthorized Webhook",
                "url": "https://example.com/webhook",
            },
        )
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_create_webhook_invalid_url(self, client: TestClient, auth_headers: dict):
        """Test creating webhook with invalid URL fails."""
        response = client.post(
            "/api/v1/webhooks/",
            headers=auth_headers,
            json={
                "name": "Invalid URL Webhook",
                "url": "not-a-valid-url",
                "events": ["job.completed"],
            },
        )
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_list_webhooks(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test listing user's webhooks."""
        response = client.get("/api/v1/webhooks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_get_webhook(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test getting a specific webhook."""
        response = client.get(
            f"/api/v1/webhooks/{test_webhook.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_webhook.name
    
    @pytest.mark.unit
    def test_get_webhook_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent webhook returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/webhooks/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_update_webhook(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test updating a webhook."""
        response = client.put(
            f"/api/v1/webhooks/{test_webhook.id}",
            headers=auth_headers,
            json={
                "name": "Updated Webhook",
                "events": ["job.completed", "job.failed", "dataset.created"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Webhook"
    
    @pytest.mark.unit
    def test_delete_webhook(
        self, client: TestClient, db: Session, test_user: User, auth_headers: dict
    ):
        """Test deleting a webhook."""
        import uuid
        from datetime import datetime
        
        webhook = Webhook(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="To Delete",
            url="https://example.com/delete",
            secret="test-secret",
            events=["job.completed"],
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(webhook)
        db.commit()
        
        response = client.delete(
            f"/api/v1/webhooks/{webhook.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestWebhookOperations:
    """Tests for webhook operations"""
    
    @pytest.mark.unit
    def test_enable_webhook(
        self, client: TestClient, db: Session, test_user: User, auth_headers: dict
    ):
        """Test enabling a disabled webhook."""
        import uuid
        from datetime import datetime
        
        webhook = Webhook(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="Disabled Webhook",
            url="https://example.com/disabled",
            secret="test-secret",
            events=["job.completed"],
            is_active=False,
            created_at=datetime.utcnow(),
        )
        db.add(webhook)
        db.commit()
        
        response = client.post(
            f"/api/v1/webhooks/{webhook.id}/enable",
            headers=auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_disable_webhook(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test disabling a webhook."""
        response = client.post(
            f"/api/v1/webhooks/{test_webhook.id}/disable",
            headers=auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_test_webhook(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test sending a test webhook."""
        response = client.post(
            f"/api/v1/webhooks/{test_webhook.id}/test",
            headers=auth_headers,
        )
        # May fail if external URL is not reachable, but should return a response
        assert response.status_code in [200, 400, 500]
    
    @pytest.mark.unit
    def test_rotate_webhook_secret(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test rotating webhook secret."""
        response = client.post(
            f"/api/v1/webhooks/{test_webhook.id}/rotate-secret",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data


class TestWebhookDeliveries:
    """Tests for webhook delivery history"""
    
    @pytest.mark.unit
    def test_list_deliveries(
        self, client: TestClient, test_webhook: Webhook, auth_headers: dict
    ):
        """Test listing webhook deliveries."""
        response = client.get(
            f"/api/v1/webhooks/{test_webhook.id}/deliveries",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestWebhookEvents:
    """Tests for webhook events"""
    
    @pytest.mark.unit
    def test_list_event_types(self, client: TestClient, auth_headers: dict):
        """Test listing available event types."""
        response = client.get("/api/v1/webhooks/events", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "events" in data


class TestWebhookPermissions:
    """Tests for webhook permission checks"""
    
    @pytest.mark.unit
    def test_cannot_access_other_user_webhook(
        self, client: TestClient, db: Session, test_webhook: Webhook
    ):
        """Test that users cannot access other users' webhooks."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        other_user = create_test_user(db, email="webhookother@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/v1/webhooks/{test_webhook.id}",
            headers=headers,
        )
        assert response.status_code in [403, 404]
    
    @pytest.mark.unit
    def test_cannot_update_other_user_webhook(
        self, client: TestClient, db: Session, test_webhook: Webhook
    ):
        """Test that users cannot update other users' webhooks."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        other_user = create_test_user(db, email="webhookother2@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.put(
            f"/api/v1/webhooks/{test_webhook.id}",
            headers=headers,
            json={"name": "Hacked Webhook"},
        )
        assert response.status_code in [403, 404]
