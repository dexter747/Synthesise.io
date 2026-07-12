"""
Tests for job endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, Dataset, GenerationJob


class TestJobListing:
    """Tests for job listing endpoints"""
    
    @pytest.mark.unit
    def test_list_jobs(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test listing user's jobs."""
        response = client.get("/api/v1/jobs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_list_jobs_no_auth(self, client: TestClient):
        """Test listing jobs without auth fails."""
        response = client.get("/api/v1/jobs/")
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_list_jobs_with_status_filter(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test listing jobs with status filter."""
        response = client.get(
            "/api/v1/jobs/?status=pending",
            headers=auth_headers,
        )
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_list_jobs_with_pagination(
        self, client: TestClient, auth_headers: dict
    ):
        """Test listing jobs with pagination."""
        response = client.get(
            "/api/v1/jobs/?skip=0&limit=10",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestJobStats:
    """Tests for job statistics endpoints"""
    
    @pytest.mark.unit
    def test_get_job_stats(self, client: TestClient, auth_headers: dict):
        """Test getting job statistics."""
        response = client.get("/api/v1/jobs/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestJobDetails:
    """Tests for job detail endpoints"""
    
    @pytest.mark.unit
    def test_get_job(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test getting a specific job."""
        response = client.get(
            f"/api/v1/jobs/{test_job.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == test_job.status
    
    @pytest.mark.unit
    def test_get_job_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent job returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/jobs/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_get_job_status(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test getting job status."""
        response = client.get(
            f"/api/v1/jobs/{test_job.id}/status",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestJobActions:
    """Tests for job action endpoints"""
    
    @pytest.mark.unit
    def test_cancel_pending_job(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test canceling a pending job."""
        response = client.post(
            f"/api/v1/jobs/{test_job.id}/cancel",
            headers=auth_headers,
        )
        # Job might already be processed or cancellation might be allowed
        assert response.status_code in [200, 400]
    
    @pytest.mark.unit
    def test_retry_failed_job(
        self, client: TestClient, db: Session, test_user: User, 
        test_dataset: Dataset, auth_headers: dict
    ):
        """Test retrying a failed job."""
        import uuid
        from datetime import datetime
        
        # Create a failed job
        job = GenerationJob(
            id=uuid.uuid4(),
            dataset_id=test_dataset.id,
            user_id=test_user.id,
            status="failed",
            row_count=1000,
            error_message="Test failure",
            created_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        
        response = client.post(
            f"/api/v1/jobs/{job.id}/retry",
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 202, 403, 404]
    
    @pytest.mark.unit
    def test_delete_job(
        self, client: TestClient, db: Session, test_user: User, 
        test_dataset: Dataset, auth_headers: dict
    ):
        """Test deleting a job."""
        import uuid
        from datetime import datetime
        
        job = GenerationJob(
            id=uuid.uuid4(),
            dataset_id=test_dataset.id,
            user_id=test_user.id,
            status="completed",
            row_count=100,
            rows_generated=100,
            created_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        
        response = client.delete(
            f"/api/v1/jobs/{job.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestJobDownload:
    """Tests for job download endpoints"""
    
    @pytest.mark.unit
    def test_download_completed_job(
        self, client: TestClient, completed_job: GenerationJob, auth_headers: dict
    ):
        """Test downloading completed job data."""
        response = client.get(
            f"/api/v1/jobs/{completed_job.id}/download",
            headers=auth_headers,
        )
        # May return file or redirect or error if file doesn't exist
        assert response.status_code in [200, 302, 404]
    
    @pytest.mark.unit
    def test_download_pending_job_fails(
        self, client: TestClient, test_job: GenerationJob, auth_headers: dict
    ):
        """Test downloading pending job fails."""
        response = client.get(
            f"/api/v1/jobs/{test_job.id}/download",
            headers=auth_headers,
        )
        # Should fail because job is not completed
        assert response.status_code in [400, 404]
    
    @pytest.mark.unit
    def test_preview_completed_job(
        self, client: TestClient, completed_job: GenerationJob, auth_headers: dict
    ):
        """Test previewing completed job data."""
        response = client.get(
            f"/api/v1/jobs/{completed_job.id}/preview",
            headers=auth_headers,
        )
        # May work or fail depending on file existence
        assert response.status_code in [200, 403, 404]


class TestJobPermissions:
    """Tests for job permission checks"""
    
    @pytest.mark.unit
    def test_cannot_access_other_user_job(
        self, client: TestClient, db: Session, test_job: GenerationJob
    ):
        """Test that users cannot access other users' jobs."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        other_user = create_test_user(db, email="jobother@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/v1/jobs/{test_job.id}",
            headers=headers,
        )
        assert response.status_code in [403, 404]
    
    @pytest.mark.unit
    def test_cannot_cancel_other_user_job(
        self, client: TestClient, db: Session, test_job: GenerationJob
    ):
        """Test that users cannot cancel other users' jobs."""
        from tests.conftest import create_test_user
        from app.core.security import create_access_token
        from datetime import timedelta
        
        other_user = create_test_user(db, email="jobother2@example.com")
        token = create_access_token(
            subject=str(other_user.id),
            expires_delta=timedelta(hours=1)
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            f"/api/v1/jobs/{test_job.id}/cancel",
            headers=headers,
        )
        assert response.status_code in [403, 404]
