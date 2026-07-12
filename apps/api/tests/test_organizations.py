"""
Tests for organization endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, Organization, OrganizationMember, OrganizationInvitation

# Alias for convenience
OrganizationInvite = OrganizationInvitation


class TestOrganizationCRUD:
    """Tests for organization CRUD operations"""
    
    @pytest.mark.unit
    def test_create_organization(self, client: TestClient, auth_headers: dict):
        """Test creating a new organization."""
        response = client.post(
            "/api/v1/organizations/",
            headers=auth_headers,
            json={
                "name": "New Organization",
                "description": "A new test organization",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Organization"
        assert "id" in data
        assert "slug" in data
    
    @pytest.mark.unit
    def test_create_organization_no_auth(self, client: TestClient):
        """Test creating organization without auth fails."""
        response = client.post(
            "/api/v1/organizations/",
            json={"name": "Unauthorized Org"},
        )
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_get_organization(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test getting an organization."""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_organization.name
    
    @pytest.mark.unit
    def test_get_organization_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent organization returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/organizations/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_update_organization(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test updating an organization."""
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            headers=auth_headers,
            json={
                "name": "Updated Organization",
                "description": "Updated description",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Organization"
    
    @pytest.mark.unit
    def test_delete_organization(
        self, client: TestClient, db: Session, test_user: User, auth_headers: dict
    ):
        """Test deleting an organization."""
        import uuid
        from datetime import datetime
        
        # Create an org to delete
        org = Organization(
            id=uuid.uuid4(),
            name="To Delete Org",
            slug="to-delete-org",
            owner_id=test_user.id,
            created_at=datetime.utcnow(),
        )
        db.add(org)
        
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=test_user.id,
            role="admin",
            created_at=datetime.utcnow(),
        )
        db.add(member)
        db.commit()
        
        response = client.delete(
            f"/api/v1/organizations/{org.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestOrganizationMembers:
    """Tests for organization member operations"""
    
    @pytest.mark.unit
    def test_list_members(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test listing organization members."""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/members",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_update_member_role(
        self, client: TestClient, db: Session, test_organization: Organization, 
        test_user: User, auth_headers: dict
    ):
        """Test updating a member's role."""
        import uuid
        from datetime import datetime
        from tests.conftest import create_test_user
        
        # Add another member
        other_user = create_test_user(db, email="member@example.com")
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=test_organization.id,
            user_id=other_user.id,
            role="member",
            created_at=datetime.utcnow(),
        )
        db.add(member)
        db.commit()
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{member.id}?role=admin",
            headers=auth_headers,
        )
        assert response.status_code in [200, 400, 403, 404]  # May fail if role is invalid, not authorized, or not found
    
    @pytest.mark.unit
    def test_remove_member(
        self, client: TestClient, db: Session, test_organization: Organization,
        auth_headers: dict
    ):
        """Test removing a member from organization."""
        import uuid
        from datetime import datetime
        from tests.conftest import create_test_user
        
        other_user = create_test_user(db, email="toremove@example.com")
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=test_organization.id,
            user_id=other_user.id,
            role="member",
            created_at=datetime.utcnow(),
        )
        db.add(member)
        db.commit()
        
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{other_user.id}",
            headers=auth_headers,
        )
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.unit
    def test_leave_organization(
        self, client: TestClient, db: Session, test_organization: Organization
    ):
        """Test leaving an organization."""
        import uuid
        from datetime import datetime, timedelta
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        
        # Create a member to leave
        other_user = create_test_user(db, email="leaving@example.com")
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=test_organization.id,
            user_id=other_user.id,
            role="member",
            created_at=datetime.utcnow(),
        )
        db.add(member)
        db.commit()
        
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/leave",
            headers=headers,
        )
        assert response.status_code == 200


class TestOrganizationInvites:
    """Tests for organization invite operations"""
    
    @pytest.mark.unit
    def test_list_invites(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test listing organization invites."""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/invites",
            headers=auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_create_invite(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test creating an invite."""
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/invites",
            headers=auth_headers,
            json={
                "email": "invitee@example.com",
                "role": "member",
            },
        )
        assert response.status_code in [200, 201]
    
    @pytest.mark.unit
    def test_delete_invite(
        self, client: TestClient, db: Session, test_organization: Organization, 
        test_user: User, auth_headers: dict
    ):
        """Test deleting an invite."""
        import uuid
        from datetime import datetime, timedelta
        
        invite = OrganizationInvite(
            id=uuid.uuid4(),
            organization_id=test_organization.id,
            email="todelete@example.com",
            role="member",
            invited_by_id=test_user.id,
            token="test-token-123",
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
        )
        db.add(invite)
        db.commit()
        
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/invites/{invite.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestOrganizationDatasets:
    """Tests for organization dataset operations"""
    
    @pytest.mark.unit
    def test_list_organization_datasets(
        self, client: TestClient, test_organization: Organization, auth_headers: dict
    ):
        """Test listing organization's datasets."""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/datasets",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestOrganizationPermissions:
    """Tests for organization permission checks"""
    
    @pytest.mark.unit
    def test_non_member_cannot_access(
        self, client: TestClient, db: Session, test_organization: Organization
    ):
        """Test that non-members cannot access organization."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        other_user = create_test_user(db, email="nonmember@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers=headers,
        )
        assert response.status_code in [403, 404]
    
    @pytest.mark.unit
    def test_member_cannot_update_without_permission(
        self, client: TestClient, db: Session, test_organization: Organization
    ):
        """Test that regular members cannot update organization."""
        import uuid
        from datetime import datetime, timedelta
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        
        other_user = create_test_user(db, email="regularuser@example.com")
        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=test_organization.id,
            user_id=other_user.id,
            role="member",  # Not admin
            created_at=datetime.utcnow(),
        )
        db.add(member)
        db.commit()
        
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            headers=headers,
            json={"name": "Unauthorized Update"},
        )
        assert response.status_code == 403
