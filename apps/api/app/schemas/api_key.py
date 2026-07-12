"""
API Key schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class APIKeyCreate(BaseSchema):
    """Create a new API key."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: list[str] = ["read", "write"]  # Available: read, write, admin, generate
    expires_at: Optional[datetime] = None
    rate_limit: Optional[int] = None  # Requests per hour, None = use default
    ip_whitelist: list[str] = []


class APIKeyUpdate(BaseSchema):
    """Update API key."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: Optional[list[str]] = None
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = None
    ip_whitelist: Optional[list[str]] = None


class APIKeyRegenerateRequest(BaseSchema):
    """Regenerate API key."""
    
    # Confirmation that old key should be invalidated
    confirm: bool = True


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class APIKeyResponse(BaseSchema, TimestampMixin):
    """API key response (without the actual key)."""
    
    id: UUID
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    key_prefix: str  # First 8 chars of key for identification
    scopes: list[str] = []
    is_active: bool = True
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None
    ip_whitelist: list[str] = []


class APIKeyCreateResponse(APIKeyResponse):
    """Response when creating API key (includes full key, shown only once)."""
    
    key: str  # Full API key - only shown once on creation


class APIKeyListResponse(PaginatedResponse[APIKeyResponse]):
    """Paginated list of API keys."""
    pass


class APIKeyUsageItem(BaseSchema):
    """API key usage record."""
    
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    response_time_ms: int
    ip_address: str


class APIKeyUsageResponse(BaseSchema):
    """API key usage stats."""
    
    key_id: UUID
    period: str = "30d"
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    requests_by_endpoint: dict = {}
    requests_by_day: list[dict] = []
    requests_by_status: dict[str, int] = {}
    recent_usage: list[APIKeyUsageItem] = []


class APIKeyValidationResponse(BaseSchema):
    """API key validation result."""
    
    valid: bool
    key_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    scopes: list[str] = []
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    error: Optional[str] = None


# =============================================================================
# ADDITIONAL ENDPOINT SCHEMAS
# =============================================================================

class APIKeyDetailResponse(BaseSchema):
    """Detailed API key response."""
    
    id: UUID
    user_id: Optional[UUID] = None
    name: str
    key_prefix: str
    scopes: list[str] = []
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None


class APIKeyCreatedResponse(BaseSchema):
    """Response when API key is created (includes full key)."""
    
    id: UUID
    name: str
    key: str  # Full key - only shown once!
    key_prefix: str
    scopes: list[str] = []
    expires_at: Optional[datetime] = None
    created_at: datetime

