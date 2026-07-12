"""
Unit tests for service layer.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import Session


class TestAuthService:
    """Tests for auth service"""
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification."""
        from app.core.security import hash_password, verify_password
        
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    @pytest.mark.unit
    def test_create_access_token(self):
        """Test access token creation."""
        from app.core.security import create_access_token
        
        user_id = str(uuid.uuid4())
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(hours=1)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.unit
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from app.core.security import create_refresh_token
        
        user_id = str(uuid.uuid4())
        token = create_refresh_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)


class TestSecurityUtils:
    """Tests for security utilities"""
    
    @pytest.mark.unit
    def test_generate_api_key(self):
        """Test API key generation."""
        from app.core.security import generate_api_key
        
        prefix, full_key, key_hash = generate_api_key()
        
        assert prefix is not None
        assert full_key is not None
        assert key_hash is not None
        assert len(full_key) >= 32
        assert full_key.startswith(prefix)
    
    @pytest.mark.unit
    def test_generate_webhook_secret(self):
        """Test webhook secret generation."""
        from app.core.security import generate_token
        
        secret = generate_token(32)
        
        assert secret is not None
        assert len(secret) >= 32
    
    @pytest.mark.unit
    def test_webhook_signature(self):
        """Test webhook signature generation and verification."""
        from app.core.security import generate_webhook_signature, verify_webhook_signature
        
        payload = '{"event": "job.completed"}'
        secret = "whsec_test123456"
        
        signature = generate_webhook_signature(payload, secret)
        
        assert signature is not None
        assert signature.startswith("sha256=")
        assert verify_webhook_signature(payload, secret, signature)


class TestValidators:
    """Tests for validators"""
    
    @pytest.mark.unit
    def test_email_validator(self):
        """Test email validation."""
        from app.utils.validators import validate_email
        
        is_valid, error = validate_email("user@example.com")
        assert is_valid is True
        
        is_valid, error = validate_email("invalid-email")
        assert is_valid is False
        
        is_valid, error = validate_email("")
        assert is_valid is False
    
    @pytest.mark.unit
    def test_password_validator(self):
        """Test password validation."""
        from app.utils.validators import validate_password
        
        # Strong password
        is_valid, errors = validate_password("SecurePass123!")
        assert is_valid
        assert len(errors) == 0
        
        # Weak password
        is_valid, errors = validate_password("weak")
        assert not is_valid
        assert len(errors) > 0
    
    @pytest.mark.unit
    def test_url_validator(self):
        """Test URL validation."""
        from app.utils.validators import validate_url
        
        is_valid, error = validate_url("https://example.com")
        assert is_valid is True
        
        is_valid, error = validate_url("http://localhost:8000")
        assert is_valid is True
        
        is_valid, error = validate_url("not-a-url")
        assert is_valid is False
    
    @pytest.mark.unit
    def test_slug_validator(self):
        """Test slug validation."""
        from app.utils.validators import validate_slug
        
        is_valid, error = validate_slug("valid-slug-123")
        assert is_valid is True
        
        is_valid, error = validate_slug("Invalid Slug!")
        assert is_valid is False


class TestHelpers:
    """Tests for helper functions"""
    
    @pytest.mark.unit
    def test_generate_slug(self):
        """Test slug generation."""
        from app.utils.helpers import generate_slug
        
        slug = generate_slug("My Test Dataset!")
        
        assert " " not in slug
        assert slug.islower() or "-" in slug
    
    @pytest.mark.unit
    def test_format_file_size(self):
        """Test file size formatting."""
        from app.utils.helpers import format_bytes
        
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1048576) == "1.00 MB"
        assert format_bytes(1073741824) == "1.00 GB"
    
    @pytest.mark.unit
    def test_paginate(self):
        """Test pagination helper."""
        from app.utils.helpers import calculate_pagination
        
        result = calculate_pagination(total=100, page=2, per_page=10)
        
        assert result["total"] == 100
        assert result["page"] == 2
        assert result["total_pages"] == 10


class TestEmailUtils:
    """Tests for email utilities"""
    
    @pytest.mark.unit
    def test_email_template_enum(self):
        """Test email template enum."""
        from app.utils.email import EmailTemplate
        
        assert EmailTemplate.WELCOME is not None
        assert EmailTemplate.PASSWORD_RESET is not None
        assert EmailTemplate.EMAIL_VERIFICATION is not None


class TestStorageUtils:
    """Tests for storage utilities"""
    
    @pytest.mark.unit
    def test_file_storage_init(self):
        """Test file storage initialization."""
        from app.utils.storage import FileStorage
        from pathlib import Path
        
        storage = FileStorage(base_path="/tmp/test")
        
        assert storage is not None
        assert str(storage.base_path) == "/tmp/test"
        assert isinstance(storage.base_path, Path)


class TestExceptions:
    """Tests for custom exceptions"""
    
    @pytest.mark.unit
    def test_synthesize_exception(self):
        """Test base exception."""
        from app.core.exceptions import SynthesizeException
        
        exc = SynthesizeException("Test error", status_code=400)
        
        assert str(exc) == "Test error"
        assert exc.status_code == 400
    
    @pytest.mark.unit
    def test_auth_exception(self):
        """Test authentication exception."""
        from app.core.exceptions import AuthenticationError
        
        exc = AuthenticationError("Invalid credentials")
        
        assert str(exc) == "Invalid credentials"
        assert exc.status_code == 401
    
    @pytest.mark.unit
    def test_validation_exception(self):
        """Test validation exception."""
        from app.core.exceptions import ValidationError
        
        exc = ValidationError("Invalid input")
        
        assert str(exc) == "Invalid input"
        assert exc.status_code == 400
    
    @pytest.mark.unit
    def test_not_found_exception(self):
        """Test not found exception."""
        from app.core.exceptions import NotFoundError
        
        exc = NotFoundError("Resource")
        
        assert "Resource" in str(exc)
        assert exc.status_code == 404
    
    @pytest.mark.unit
    def test_permission_exception(self):
        """Test permission exception."""
        from app.core.exceptions import InsufficientPermissionsError
        
        exc = InsufficientPermissionsError()
        
        assert "permissions" in str(exc).lower()
        assert exc.status_code == 403
    
    @pytest.mark.unit
    def test_rate_limit_exception(self):
        """Test rate limit exception."""
        from app.core.exceptions import RateLimitError
        
        exc = RateLimitError()
        
        assert "rate limit" in str(exc).lower()
        assert exc.status_code == 429
        assert exc.status_code == 429
