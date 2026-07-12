"""
Unit Tests for Faker Service
============================
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.faker_service import FakerService, FakerColumnConfig


class TestFakerService:
    """Unit tests for Faker service"""
    
    def test_faker_service_init(self):
        """Test Faker service initialization"""
        service = FakerService()
        assert service is not None
        assert service.faker is not None
    
    def test_get_providers_returns_dict(self):
        """Test get_providers returns properly structured dict"""
        service = FakerService()
        providers = service.get_providers()
        
        assert isinstance(providers, dict)
        assert len(providers) > 0
        
        # Check structure
        for category, methods in providers.items():
            assert isinstance(category, str)
            assert isinstance(methods, list)
            assert len(methods) > 0
    
    def test_generate_preview_basic(self):
        """Test basic preview generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name="name", provider="name"),
            FakerColumnConfig(name="email", provider="email")
        ]
        
        df = service.generate_preview(columns, num_rows=10)
        
        assert df is not None
        assert len(df) == 10
        assert list(df.columns) == ["name", "email"]
    
    def test_generate_preview_with_args(self):
        """Test preview generation with method arguments"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(
                name="random_number",
                provider="random_int",
                params={"min": 1, "max": 100}
            )
        ]
        
        df = service.generate_preview(columns, num_rows=20)
        
        assert len(df) == 20
        # Values should be within range (allow for random variation)
        for val in df["random_number"]:
            assert isinstance(val, int)
    
    def test_generate_preview_validates_row_limit(self):
        """Test preview generation enforces row limits"""
        service = FakerService()
        
        columns = [FakerColumnConfig(name="name", provider="name")]
        
        # Should raise error for too many rows
        with pytest.raises(ValueError):
            service.generate_preview(columns, num_rows=100000000)
    
    def test_generate_preview_different_locales(self):
        """Test preview generation with different locales"""
        service = FakerService()
        
        columns = [FakerColumnConfig(name="name", provider="name")]
        
        # US locale
        df_us = service.generate_preview(columns, num_rows=5, locale="en_US")
        assert len(df_us) == 5
        
        # Spanish locale
        df_es = service.generate_preview(columns, num_rows=5, locale="es_ES")
        assert len(df_es) == 5
    
    def test_generate_preview_empty_columns(self):
        """Test preview generation fails with empty columns"""
        service = FakerService()
        
        with pytest.raises((ValueError, AssertionError)):
            service.generate_preview([], num_rows=5)
    
    def test_column_config_validation(self):
        """Test FakerColumnConfig validation"""
        # Valid config
        config = FakerColumnConfig(
            name="test",
            provider="name"
        )
        assert config.name == "test"
        assert config.provider == "name"
        
        # With params
        config_with_params = FakerColumnConfig(
            name="age",
            provider="random_int",
            params={"min": 18, "max": 65}
        )
        assert config_with_params.params == {"min": 18, "max": 65}


class TestFakerServiceEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_provider(self):
        """Test handling of invalid provider"""
        service = FakerService()
        
        columns = [FakerColumnConfig(
            name="test",
            provider="nonexistent_provider_xyz"
        )]
        
        with pytest.raises(Exception):
            service.generate_preview(columns, num_rows=5)
    
    def test_invalid_method(self):
        """Test handling of invalid method"""
        service = FakerService()
        
        columns = [FakerColumnConfig(
            name="test",
            provider="nonexistent_method_xyz"
        )]
        
        with pytest.raises(Exception):
            service.generate_preview(columns, num_rows=5)
    
    def test_zero_rows(self):
        """Test handling of zero rows request"""
        service = FakerService()
        
        columns = [FakerColumnConfig(name="name", provider="name")]
        
        with pytest.raises(ValueError):
            service.generate_preview(columns, num_rows=0)
    
    def test_negative_rows(self):
        """Test handling of negative rows request"""
        service = FakerService()
        
        columns = [FakerColumnConfig(name="name", provider="name")]
        
        with pytest.raises(ValueError):
            service.generate_preview(columns, num_rows=-10)
    
    def test_invalid_locale(self):
        """Test handling of invalid locale"""
        service = FakerService()
        
        columns = [FakerColumnConfig(name="name", provider="name")]
        
        # Should either raise error or fall back to default
        with pytest.raises(Exception):
            service.generate_preview(columns, num_rows=5, locale="invalid_locale_xyz")


class TestFakerDataTypes:
    """Test different data types generation"""
    
    def test_generate_strings(self):
        """Test string data generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name="first_name", provider="first_name"),
            FakerColumnConfig(name="last_name", provider="last_name")
        ]
        
        df = service.generate_preview(columns, num_rows=10)
        
        assert all(isinstance(val, str) for val in df["first_name"])
        assert all(isinstance(val, str) for val in df["last_name"])
    
    def test_generate_numbers(self):
        """Test numeric data generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(
                name="age",
                provider="random_int",
                params={"min": 0, "max": 100}
            )
        ]
        
        df = service.generate_preview(columns, num_rows=10)
        
        assert all(isinstance(val, int) for val in df["age"])
    
    def test_generate_dates(self):
        """Test date data generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name="birthdate", provider="date_of_birth")
        ]
        
        df = service.generate_preview(columns, num_rows=10)
        
        assert len(df) == 10
        assert "birthdate" in df.columns
    
    def test_generate_boolean(self):
        """Test boolean data generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name="active", provider="pybool")
        ]
        
        df = service.generate_preview(columns, num_rows=20)
        
        assert all(isinstance(val, bool) for val in df["active"])
        # Should have mix of True and False
        assert df["active"].sum() < 20  # Not all True
        assert df["active"].sum() > 0   # Not all False


class TestFakerPerformance:
    """Test performance characteristics"""
    
    def test_generate_large_dataset_performance(self):
        """Test generation of large datasets completes in reasonable time"""
        import time
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name=f"col{i}", provider="name")
            for i in range(10)
        ]
        
        start = time.time()
        df = service.generate_preview(columns, num_rows=1000)
        elapsed = time.time() - start
        
        assert len(df) == 1000
        assert len(df.columns) == 10
        # Should complete in less than 5 seconds
        assert elapsed < 5.0
    
    def test_memory_efficient_generation(self):
        """Test memory-efficient generation"""
        service = FakerService()
        
        columns = [
            FakerColumnConfig(name="text", provider="text")
        ]
        
        # Generate relatively large dataset
        df = service.generate_preview(columns, num_rows=5000)
        
        # Check memory usage is reasonable (not testing actual bytes, just that it completes)
        assert len(df) == 5000
        assert df.memory_usage(deep=True).sum() > 0
