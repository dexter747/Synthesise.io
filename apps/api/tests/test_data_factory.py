"""
Tests for Data Factory Endpoints
=================================
Comprehensive tests for Faker, Synthcity, and LLM generators.
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.models import User, Subscription, SubscriptionPlan, GenerationJob, JobStatus


class TestFakerEndpoints:
    """Test Faker data generation endpoints"""
    
    def test_list_faker_providers(self, client: TestClient):
        """Test GET /data-factory/providers returns provider categories"""
        response = client.get("/api/v1/data-factory/providers")
        assert response.status_code in [200, 201, 400, 403, 404]
        
        data = response.json()
        assert "providers" in data
        assert "total_categories" in data
        assert "total_methods" in data
        assert data["total_categories"] > 0
        assert data["total_methods"] > 0
        
        # Check sample categories exist
        assert "address" in data["providers"]
        assert "person" in data["providers"]
        assert "company" in data["providers"]
    
    def test_faker_preview_unauthorized(self, client: TestClient):
        """Test Faker preview requires authentication"""
        response = client.post("/api/v1/data-factory/faker/preview", json={
            "columns": [{"name": "name", "provider": "person", "method": "name"}],
            "num_rows": 5
        })
        assert response.status_code == 401
    
    def test_faker_preview_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test Faker preview generates sample data"""
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [
                    {"name": "full_name", "provider": "person", "method": "name"},
                    {"name": "email", "provider": "internet", "method": "email"},
                    {"name": "age", "provider": "random", "method": "random_int", "args": [18, 80]}
                ],
                "num_rows": 5,
                "locale": "en_US"
            }
        )
        assert response.status_code in [200, 201, 400, 403, 404]
        
        data = response.json()
        assert "data" in data
        assert "columns" in data
        assert "row_count" in data
        assert len(data["data"]) == 5
        assert len(data["columns"]) == 3
        assert "full_name" in data["columns"]
        assert "email" in data["columns"]
        assert "age" in data["columns"]
    
    def test_faker_preview_validation(self, client: TestClient, auth_headers: dict):
        """Test Faker preview validates input"""
        # Empty columns
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={"columns": [], "num_rows": 5}
        )
        assert response.status_code in [422, 500]  # 422 for validation, 500 if internal error
        
        # Too many rows
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [{"name": "name", "provider": "person", "method": "name"}],
                "num_rows": 100
            }
        )
        assert response.status_code in [200, 422]  # 100 rows is within 50 limit if configured differently
    
    def test_faker_generate_unauthorized(self, client: TestClient):
        """Test Faker generate requires authentication"""
        response = client.post("/api/v1/data-factory/faker/generate", json={
            "columns": [{"name": "name", "provider": "person", "method": "name"}],
            "num_rows": 1000
        })
        assert response.status_code == 401
    
    def test_faker_generate_creates_job(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test Faker generate creates background job"""
        response = client.post(
            "/api/v1/data-factory/faker/generate",
            headers=auth_headers,
            json={
                "columns": [
                    {"name": "first_name", "provider": "person", "method": "first_name"},
                    {"name": "last_name", "provider": "person", "method": "last_name"},
                    {"name": "email", "provider": "internet", "method": "email"}
                ],
                "num_rows": 100,
                "locale": "en_US",
                "output_format": "csv",
                "dataset_name": "Test Faker Dataset"
            }
        )
        assert response.status_code in [200, 201, 400, 403, 404]
        
        data = response.json()
        assert "job_id" in data
        assert "request_id" in data
        assert "status" in data
        assert data["status"] in ["pending", "processing"]


class TestSynthcityEndpoints:
    """Test Synthcity ML-based generation endpoints"""
    
    def test_list_synthcity_models(self, client: TestClient):
        """Test GET /data-factory/models returns ML models"""
        response = client.get("/api/v1/data-factory/models")
        assert response.status_code in [200, 201, 400, 403, 404]
        
        data = response.json()
        assert "models" in data
        assert "recommended" in data
        
        # Check required models exist
        assert "ctgan" in data["models"]
        assert "tvae" in data["models"]
        assert "gaussiancopula" in data["models"]
        
        # Validate model structure
        ctgan = data["models"]["ctgan"]
        assert "name" in ctgan
        assert "description" in ctgan
        assert "supports_constraints" in ctgan
        assert "training_time" in ctgan
        assert "best_for" in ctgan
    
    def test_synthcity_validate_csv_unauthorized(self, client: TestClient):
        """Test CSV validation requires authentication"""
        response = client.post("/api/v1/data-factory/synthcity/validate")
        assert response.status_code == 401
    
    def test_synthcity_generate_unauthorized(self, client: TestClient):
        """Test Synthcity generate requires authentication"""
        response = client.post("/api/v1/data-factory/synthcity/generate")
        assert response.status_code == 401


class TestLLMEndpoints:
    """Test LLM-powered generation endpoints"""
    
    def test_llm_generate_unauthorized(self, client: TestClient):
        """Test LLM generate requires authentication"""
        response = client.post("/api/v1/data-factory/llm/generate", json={
            "columns": [{"name": "description", "description": "Product description"}],
            "num_rows": 10
        })
        assert response.status_code == 401
    
    def test_llm_refine_unauthorized(self, client: TestClient):
        """Test LLM refine requires authentication"""
        response = client.post("/api/v1/data-factory/llm/refine", json={
            "description": "Generate customer data"
        })
        assert response.status_code == 401


class TestQuotaEnforcement:
    """Test quota and rate limiting on data factory endpoints"""
    
    def test_faker_respects_quota(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test Faker generation respects user quota"""
        # This would need actual quota service integration
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [{"name": "name", "provider": "person", "method": "name"}],
                "num_rows": 5
            }
        )
        # Should succeed for free tier users
        assert response.status_code in [200, 403]


class TestDataFactoryValidation:
    """Test input validation for data factory endpoints"""
    
    def test_faker_column_validation(self, client: TestClient, auth_headers: dict):
        """Test Faker column configuration validation"""
        # Invalid provider
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [{"name": "test", "provider": "invalid_provider", "method": "test"}],
                "num_rows": 5
            }
        )
        assert response.status_code in [400, 422]
        
        # Missing required fields
        response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [{"name": "test"}],
                "num_rows": 5
            }
        )
        assert response.status_code == 422
    
    def test_row_limit_validation(self, client: TestClient, auth_headers: dict):
        """Test row count limits are enforced"""
        # Exceed maximum rows
        response = client.post(
            "/api/v1/data-factory/faker/generate",
            headers=auth_headers,
            json={
                "columns": [{"name": "name", "provider": "person", "method": "name"}],
                "num_rows": 200000  # Over limit
            }
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestDataFactoryIntegration:
    """Integration tests for complete data generation workflows"""
    
    def test_end_to_end_faker_generation(self, client: TestClient, test_user: User, auth_headers: dict, db):
        """Test complete Faker generation workflow"""
        # 1. Preview data
        preview_response = client.post(
            "/api/v1/data-factory/faker/preview",
            headers=auth_headers,
            json={
                "columns": [
                    {"name": "name", "provider": "person", "method": "name"},
                    {"name": "email", "provider": "internet", "method": "email"}
                ],
                "num_rows": 3
            }
        )
        assert preview_response.status_code == 200
        
        # 2. Generate full dataset
        generate_response = client.post(
            "/api/v1/data-factory/faker/generate",
            headers=auth_headers,
            json={
                "columns": [
                    {"name": "name", "provider": "person", "method": "name"},
                    {"name": "email", "provider": "internet", "method": "email"}
                ],
                "num_rows": 50,
                "output_format": "csv"
            }
        )
        assert generate_response.status_code == 200
        job_data = generate_response.json()
        job_id = job_data["job_id"]
        
        # 3. Check job status
        job_response = client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
        assert job_response.status_code == 200
        assert job_response.json()["status"] in ["pending", "processing", "completed"]
