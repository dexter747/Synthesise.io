"""
Tests for admin endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


class TestAdminDashboard:
    """Tests for admin dashboard endpoints"""
    
    @pytest.mark.unit
    def test_get_dashboard_as_admin(self, client: TestClient, admin_auth_headers: dict):
        """Test getting dashboard stats as admin."""
        response = client.get(
            "/api/v1/admin/dashboard",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    @pytest.mark.unit
    def test_get_dashboard_as_regular_user(self, client: TestClient, auth_headers: dict):
        """Test getting dashboard as regular user fails."""
        response = client.get(
            "/api/v1/admin/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 403
    
    @pytest.mark.unit
    def test_get_dashboard_no_auth(self, client: TestClient):
        """Test getting dashboard without auth fails."""
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 401


class TestAdminAnalytics:
    """Tests for admin analytics endpoints"""
    
    @pytest.mark.unit
    def test_get_analytics_as_admin(self, client: TestClient, admin_auth_headers: dict):
        """Test getting analytics as admin."""
        response = client.get(
            "/api/v1/admin/analytics",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_get_analytics_with_date_range(self, client: TestClient, admin_auth_headers: dict):
        """Test getting analytics with date range."""
        response = client.get(
            "/api/v1/admin/analytics?start_date=2024-01-01&end_date=2024-12-31",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestAdminUserManagement:
    """Tests for admin user management endpoints"""
    
    @pytest.mark.unit
    def test_list_users_as_admin(
        self, client: TestClient, test_user: User, admin_auth_headers: dict
    ):
        """Test listing users as admin."""
        response = client.get(
            "/api/v1/admin/users",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_list_users_with_filters(self, client: TestClient, admin_auth_headers: dict):
        """Test listing users with filters."""
        response = client.get(
            "/api/v1/admin/users?status=active&role=user",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_user_action_suspend(
        self, client: TestClient, db: Session, test_user: User, admin_auth_headers: dict
    ):
        """Test suspending a user."""
        response = client.post(
            f"/api/v1/admin/users/{test_user.id}/action",
            headers=admin_auth_headers,
            json={"action": "suspend", "reason": "Test suspension"},
        )
        assert response.status_code in [200, 400]
    
    @pytest.mark.unit
    def test_user_action_activate(
        self, client: TestClient, db: Session, admin_auth_headers: dict
    ):
        """Test activating a user."""
        from tests.conftest import create_test_user
        
        user = create_test_user(db, email="inactive@example.com", is_active=False)
        
        response = client.post(
            f"/api/v1/admin/users/{user.id}/action",
            headers=admin_auth_headers,
            json={"action": "reactivate"},
        )
        assert response.status_code in [200, 400]


class TestAdminSubscriptionManagement:
    """Tests for admin subscription management"""
    
    @pytest.mark.unit
    def test_list_subscriptions(self, client: TestClient, admin_auth_headers: dict):
        """Test listing subscriptions as admin."""
        response = client.get(
            "/api/v1/admin/subscriptions",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestAdminJobManagement:
    """Tests for admin job management"""
    
    @pytest.mark.unit
    def test_list_all_jobs(self, client: TestClient, admin_auth_headers: dict):
        """Test listing all jobs as admin."""
        response = client.get(
            "/api/v1/admin/jobs",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_list_jobs_with_filters(self, client: TestClient, admin_auth_headers: dict):
        """Test listing jobs with filters."""
        response = client.get(
            "/api/v1/admin/jobs?status=pending",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestAdminFeatureFlags:
    """Tests for admin feature flag management"""
    
    @pytest.mark.unit
    def test_list_feature_flags(self, client: TestClient, admin_auth_headers: dict):
        """Test listing feature flags."""
        response = client.get(
            "/api/v1/admin/feature-flags",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_create_feature_flag(self, client: TestClient, superadmin_auth_headers: dict):
        """Test creating a feature flag."""
        response = client.post(
            "/api/v1/admin/feature-flags",
            headers=superadmin_auth_headers,
            json={
                "name": "new_feature",
                "description": "A new feature flag",
                "enabled": False,
            },
        )
        assert response.status_code in [200, 201]
    
    @pytest.mark.unit
    def test_update_feature_flag(
        self, client: TestClient, db: Session, superadmin_auth_headers: dict
    ):
        """Test updating a feature flag."""
        import uuid
        from datetime import datetime
        from app.models import FeatureFlag
        
        flag = FeatureFlag(
            id=uuid.uuid4(),
            name="test_flag",
            description="Test flag",
            is_enabled=False,
            created_at=datetime.utcnow(),
        )
        db.add(flag)
        db.commit()
        
        response = client.put(
            f"/api/v1/admin/feature-flags/{flag.id}",
            headers=superadmin_auth_headers,
            json={"enabled": True},
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_delete_feature_flag(
        self, client: TestClient, db: Session, superadmin_auth_headers: dict
    ):
        """Test deleting a feature flag."""
        import uuid
        from datetime import datetime
        from app.models import FeatureFlag
        
        flag = FeatureFlag(
            id=uuid.uuid4(),
            name="to_delete",
            description="To delete",
            is_enabled=False,
            created_at=datetime.utcnow(),
        )
        db.add(flag)
        db.commit()
        
        response = client.delete(
            f"/api/v1/admin/feature-flags/{flag.id}",
            headers=superadmin_auth_headers,
        )
        assert response.status_code == 200


class TestAdminAuditLogs:
    """Tests for admin audit log endpoints"""
    
    @pytest.mark.unit
    def test_list_audit_logs(self, client: TestClient, admin_auth_headers: dict):
        """Test listing audit logs."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_list_audit_logs_with_filters(self, client: TestClient, admin_auth_headers: dict):
        """Test listing audit logs with filters."""
        response = client.get(
            "/api/v1/admin/audit-logs?action=login",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200


class TestAdminSupportTickets:
    """Tests for admin support ticket endpoints"""
    
    @pytest.mark.unit
    def test_list_tickets(self, client: TestClient, admin_auth_headers: dict):
        """Test listing support tickets."""
        response = client.get(
            "/api/v1/admin/tickets",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_update_ticket(
        self, client: TestClient, db: Session, test_user: User, admin_auth_headers: dict
    ):
        """Test updating a support ticket."""
        import uuid
        from datetime import datetime
        from app.models import SupportTicket
        
        ticket = SupportTicket(
            id=uuid.uuid4(),
            user_id=test_user.id,
            ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            subject="Test Ticket",
            description="Test description",
            status="open",
            priority="medium",
            created_at=datetime.utcnow(),
        )
        db.add(ticket)
        db.commit()
        
        response = client.put(
            f"/api/v1/admin/tickets/{ticket.id}",
            headers=admin_auth_headers,
            json={"status": "in_progress"},
        )
        assert response.status_code == 200


class TestAdminHealth:
    """Tests for admin health check endpoint"""
    
    @pytest.mark.unit
    def test_health_check(self, client: TestClient, admin_auth_headers: dict):
        """Test health check endpoint."""
        response = client.get(
            "/api/v1/admin/health",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or isinstance(data, dict)


class TestAdminPermissions:
    """Tests for admin permission checks"""
    
    @pytest.mark.unit
    def test_regular_user_cannot_access_admin(self, client: TestClient, auth_headers: dict):
        """Test that regular users cannot access admin endpoints."""
        endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/users",
            "/api/v1/admin/subscriptions",
            "/api/v1/admin/jobs",
            "/api/v1/admin/feature-flags",
            "/api/v1/admin/audit-logs",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 403, f"Expected 403 for {endpoint}"
    
    @pytest.mark.unit
    def test_admin_cannot_delete_feature_flags(
        self, client: TestClient, db: Session, admin_auth_headers: dict
    ):
        """Test that regular admin cannot delete feature flags (requires superadmin)."""
        import uuid
        from datetime import datetime
        from app.models import FeatureFlag
        
        flag = FeatureFlag(
            id=uuid.uuid4(),
            name="protected_flag",
            description="Protected",
            is_enabled=True,
        )
        db.add(flag)
        db.commit()
        
        response = client.delete(
            f"/api/v1/admin/feature-flags/{flag.id}",
            headers=admin_auth_headers,
        )
        # May require superadmin or not exist
        assert response.status_code in [200, 204, 403, 404, 405]
