"""
Organization schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, HttpUrl

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# ORGANIZATION SCHEMAS
# =============================================================================

class OrganizationCreate(BaseSchema):
    """Create a new organization."""
    
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=100, pattern="^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=500)
    website: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, pattern="^(1-10|11-50|51-200|201-500|501-1000|1001+)$")


class OrganizationUpdate(BaseSchema):
    """Update organization."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, pattern="^(1-10|11-50|51-200|201-500|501-1000|1001+)$")


class OrganizationSettingsUpdate(BaseSchema):
    """Update organization settings."""
    
    default_data_retention_days: Optional[int] = Field(None, ge=1, le=365)
    allow_public_datasets: Optional[bool] = None
    require_mfa: Optional[bool] = None
    allowed_domains: Optional[list[str]] = None
    ip_whitelist: Optional[list[str]] = None


class OrganizationSettings(BaseSchema):
    """Organization settings."""
    
    default_data_retention_days: int = 30
    allow_public_datasets: bool = False
    require_mfa: bool = False
    allowed_domains: list[str] = []
    ip_whitelist: list[str] = []


class OrganizationResponse(BaseSchema, TimestampMixin):
    """Organization response."""
    
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[UUID] = None


class OrganizationDetailResponse(OrganizationResponse):
    """Detailed organization response."""
    
    billing_email: Optional[str] = None
    settings: Optional[OrganizationSettings] = None
    members_count: int = 0
    datasets_count: int = 0
    current_usage: Optional[dict] = None


class OrganizationListResponse(PaginatedResponse[OrganizationResponse]):
    """Paginated list of organizations."""
    pass


# =============================================================================
# ORGANIZATION MEMBER SCHEMAS
# =============================================================================

class OrganizationMemberCreate(BaseSchema):
    """Add member to organization."""
    
    email: EmailStr
    role: str = Field("member", pattern="^(admin|member|viewer)$")


class OrganizationInviteCreate(BaseSchema):
    """Invite user to organization."""
    
    email: EmailStr
    role: str = Field("member", pattern="^(admin|member|viewer)$")


class OrganizationMemberUpdate(BaseSchema):
    """Update member role."""
    
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class OrganizationMemberResponse(BaseSchema):
    """Organization member response."""
    
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    joined_at: datetime
    invited_by: Optional[UUID]


class OrganizationMemberListResponse(PaginatedResponse[OrganizationMemberResponse]):
    """Paginated list of organization members."""
    pass


# =============================================================================
# ORGANIZATION INVITE SCHEMAS
# =============================================================================

class OrganizationInviteResponse(BaseSchema):
    """Organization invite response."""
    
    id: UUID
    organization_id: UUID
    organization_name: str
    email: str
    role: str
    status: str
    invited_by_id: UUID
    invited_by_name: Optional[str]
    created_at: datetime
    expires_at: datetime


class OrganizationInviteListResponse(PaginatedResponse[OrganizationInviteResponse]):
    """List of pending invites."""
    pass


class AcceptInviteRequest(BaseSchema):
    """Accept organization invite."""
    
    token: str


# =============================================================================
# ORGANIZATION STATS
# =============================================================================

class OrganizationStatsResponse(BaseSchema):
    """Organization statistics."""
    
    members_count: int = 0
    active_members_count: int = 0
    datasets_count: int = 0
    total_rows_generated: int = 0
    total_jobs: int = 0
    completed_jobs: int = 0
    api_calls_this_month: int = 0
    storage_used_bytes: int = 0
    
    # Limits from subscription
    row_limit: int = 0
    storage_limit_bytes: int = 0
    api_calls_limit: int = 0
    members_limit: int = 0


class OrganizationUsageResponse(BaseSchema):
    """Organization usage breakdown."""
    
    period_start: datetime
    period_end: datetime
    
    # Usage by category
    rows_generated: int = 0
    api_calls: int = 0
    storage_bytes: int = 0
    
    # Usage by member
    usage_by_member: list[dict] = []
    
    # Daily breakdown
    daily_usage: list[dict] = []
