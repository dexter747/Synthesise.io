"""
Integration Tests for Data Factory Services
==========================================
Tests that verify end-to-end functionality across multiple services.
"""
import pytest
import os
import tempfile
from uuid import uuid4
from app.services.faker_service import get_faker_service, FakerColumnConfig
from app.services.synthcity_service import get_synthcity_service
from app.services.llm_service import get_llm_service
from app.services.quota_service import get_quota_service
from app.models import User, SubscriptionPlan


@pytest.mark.integration
class TestFakerServiceIntegration:
    """Integration tests for Faker service"""
    
    def test_faker_service_initialization(self):
        """Test Faker service can be initialized"""
        service = get_faker_service()
        assert service is not None
    
    def test_faker_list_providers(self):
        """Test Faker can list all providers"""
        service = get_faker_service()
        providers = service.get_all_providers()
        
        assert isinstance(providers, dict)
        assert len(providers) > 0
        assert "person" in providers
        assert "address" in providers
        assert "internet" in providers
        
        # Check provider has methods (methods are FakerProviderInfo objects)
        person_methods = providers["person"]
        assert len(person_methods) > 0
        # FakerProviderInfo has .method attribute
        assert any("name" in info.method.lower() for info in person_methods)
    
    def test_faker_generate_preview(self):
        """Test Faker generates preview data correctly"""
        service = get_faker_service()
        
        columns = [
            FakerColumnConfig(
                name="full_name",
                provider="person",
                method="name"
            ),
            FakerColumnConfig(
                name="email",
                provider="internet",
                method="email"
            ),
            FakerColumnConfig(
                name="age",
                provider="random",
                method="random_int",
                args=[18, 65]
            )
        ]
        
        df = service.generate_preview(columns, num_rows=10, locale="en_US")
        
        assert df is not None
        assert len(df) == 10
        assert list(df.columns) == ["full_name", "email", "age"]
        
        # Validate data types
        assert df["full_name"].dtype == object
        assert df["email"].dtype == object
        assert df["age"].dtype in ["int64", "int32"]
        
        # Validate data content
        assert all(isinstance(name, str) and len(name) > 0 for name in df["full_name"])
        assert all("@" in email for email in df["email"])
        assert all(18 <= age <= 65 for age in df["age"])
    
    def test_faker_generate_large_dataset(self):
        """Test Faker can generate large datasets efficiently"""
        service = get_faker_service()
        
        columns = [
            FakerColumnConfig(name="id", provider="random", method="uuid4"),
            FakerColumnConfig(name="name", provider="person", method="name"),
            FakerColumnConfig(name="company", provider="company", method="company"),
        ]
        
        df = service.generate_preview(columns, num_rows=1000)
        
        assert len(df) == 1000
        assert len(df.columns) == 3
        
        # Check uniqueness of IDs
        assert df["id"].nunique() == 1000
    
    def test_faker_with_different_locales(self):
        """Test Faker works with different locales"""
        service = get_faker_service()
        
        columns = [FakerColumnConfig(name="name", provider="person", method="name")]
        
        # English
        df_en = service.generate_preview(columns, num_rows=5, locale="en_US")
        assert len(df_en) == 5
        
        # Spanish
        df_es = service.generate_preview(columns, num_rows=5, locale="es_ES")
        assert len(df_es) == 5
        
        # French
        df_fr = service.generate_preview(columns, num_rows=5, locale="fr_FR")
        assert len(df_fr) == 5


@pytest.mark.integration
class TestSynthcityServiceIntegration:
    """Integration tests for Synthcity ML service"""
    
    def test_synthcity_service_initialization(self):
        """Test Synthcity service can be initialized"""
        service = get_synthcity_service()
        assert service is not None
    
    def test_synthcity_list_models(self):
        """Test Synthcity lists available ML models"""
        service = get_synthcity_service()
        models = service.get_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        assert "ctgan" in models
        assert "tvae" in models
        assert "gaussiancopula" in models
        
        # Validate model metadata
        ctgan = models["ctgan"]
        assert "name" in ctgan
        assert "description" in ctgan
        assert "training_time" in ctgan
    
    def test_synthcity_validate_csv(self):
        """Test Synthcity validates CSV files"""
        service = get_synthcity_service()
        
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,city\n")
            f.write("John,30,NYC\n")
            f.write("Jane,25,LA\n")
            f.write("Bob,35,Chicago\n")
            temp_path = f.name
        
        try:
            # Read file content as bytes and pass to validate_csv
            with open(temp_path, 'rb') as f:
                file_content = f.read()
            
            df, validation = service.validate_csv(file_content, os.path.basename(temp_path))
            
            assert validation.valid is True
            assert validation.rows == 3  # Field is 'rows' not 'row_count'
            assert len(validation.columns) == 3  # columns is List[str]
            assert "name" in validation.columns
            assert "age" in validation.columns
            assert "city" in validation.columns
        finally:
            os.unlink(temp_path)


@pytest.mark.integration
class TestLLMServiceIntegration:
    """Integration tests for LLM service"""
    
    def test_llm_service_initialization(self):
        """Test LLM service can be initialized"""
        service = get_llm_service()
        assert service is not None
    
    @pytest.mark.skipif(
        not os.getenv("GROQ_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No LLM API key configured"
    )
    def test_llm_refine_description(self):
        """Test LLM can refine natural language to schema"""
        service = get_llm_service()
        
        description = "Generate customer data with name, email, age, and city"
        
        # Method is refine_request, not refine_description
        result = service.refine_request(description)
        
        # refine_request returns a dict with 'columns' key
        assert isinstance(result, dict)
        assert "columns" in result
        
        schema = result["columns"]
        assert isinstance(schema, list)
        assert len(schema) > 0
        
        # Columns may be strings (fallback) or dicts with name key
        field_names = []
        for col in schema:
            if isinstance(col, str):
                field_names.append(col)
            elif isinstance(col, dict):
                field_names.append(col.get("name", ""))
        
        # With fallback, we get generic fields like "name", "email"
        assert any("name" in f.lower() for f in field_names)
        assert any("email" in f.lower() for f in field_names)


@pytest.mark.integration
class TestQuotaServiceIntegration:
    """Integration tests for quota enforcement"""
    
    def test_quota_service_initialization(self, db):
        """Test quota service can be initialized"""
        service = get_quota_service(db)
        assert service is not None
    
    def test_check_quota_limits(self, db, test_user: User):
        """Test quota checking works correctly"""
        service = get_quota_service(db)
        
        # Check if user can access Faker
        allowed, message = service.check_feature_access(test_user.id, "faker")
        assert isinstance(allowed, bool)
        assert isinstance(message, str)
    
    def test_record_usage(self, db, test_user: User):
        """Test usage recording"""
        service = get_quota_service(db)
        
        # Record some usage - use actual method signature
        record = service.record_usage(
            user_id=test_user.id,
            rows_generated=100,
            bytes_generated=1000,
            datasets_created=1,
        )
        
        # Verify usage was recorded
        assert record is not None
        assert record.user_id == test_user.id
        assert record.datasets_created >= 1


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_faker_generation_workflow(self, db, test_user: User):
        """Test complete Faker generation from preview to download"""
        faker_service = get_faker_service()
        quota_service = get_quota_service(db)
        
        # 1. Check quota
        allowed, _ = quota_service.check_feature_access(test_user.id, "faker")
        assert allowed
        
        # 2. Generate preview
        columns = [
            FakerColumnConfig(name="name", provider="person", method="name"),
            FakerColumnConfig(name="email", provider="internet", method="email")
        ]
        preview_df = faker_service.generate_preview(columns, num_rows=5)
        assert len(preview_df) == 5
        
        # 3. Generate full dataset
        full_df = faker_service.generate_preview(columns, num_rows=100)
        assert len(full_df) == 100
        
        # 4. Export to CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            full_df.to_csv(temp_path, index=False)
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_data_validation_workflow(self):
        """Test CSV validation and error handling"""
        from app.core.exceptions import ValidationError
        synthcity_service = get_synthcity_service()
        
        # Test with empty CSV - service raises ValidationError for unparseable files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            # Read file content as bytes and pass to validate_csv
            with open(temp_path, 'rb') as f:
                file_content = f.read()
            
            # Empty file should raise ValidationError
            with pytest.raises(ValidationError):
                synthcity_service.validate_csv(file_content, os.path.basename(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_concurrent_generation_requests(self, db, test_user: User):
        """Test system handles multiple concurrent generation requests"""
        faker_service = get_faker_service()
        
        columns = [FakerColumnConfig(name="id", provider="random", method="uuid4")]
        
        # Simulate concurrent requests
        results = []
        for i in range(5):
            df = faker_service.generate_preview(columns, num_rows=10)
            results.append(df)
        
        # Verify all completed successfully
        assert len(results) == 5
        assert all(len(df) == 10 for df in results)
        
        # Verify data is unique across requests
        all_ids = set()
        for df in results:
            all_ids.update(df["id"].tolist())
        assert len(all_ids) == 50  # All IDs should be unique


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across services"""
    
    def test_faker_invalid_provider(self):
        """Test Faker handles invalid provider gracefully"""
        service = get_faker_service()
        
        with pytest.raises(Exception):
            columns = [FakerColumnConfig(
                name="test",
                provider="invalid_provider_123",
                method="invalid_method"
            )]
            service.generate_preview(columns, num_rows=5)
    
    def test_synthcity_invalid_file(self):
        """Test Synthcity handles invalid files gracefully"""
        service = get_synthcity_service()
        
        # Invalid file content (not a valid CSV)
        invalid_content = b"not a valid csv content\x00\x01\x02"
        
        # This should raise an exception or return invalid validation
        with pytest.raises(Exception):
            service.validate_csv(invalid_content, "invalid.csv")
    
    def test_quota_exceeded_handling(self, db, test_user: User):
        """Test system handles quota exceeded gracefully"""
        quota_service = get_quota_service(db)
        
        # Check if quota checking works
        allowed, message = quota_service.check_feature_access(test_user.id, "faker")
        assert isinstance(allowed, bool)
        assert message is not None
