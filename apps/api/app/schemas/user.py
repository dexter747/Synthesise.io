"""
User schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class UserCreate(BaseSchema):
    """Create a new user (admin use)."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: str = "user"
    status: str = "active"


class UserUpdate(BaseSchema):
    """Update user profile."""
    
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    locale: Optional[str] = Field(None, max_length=10)


class UserPreferencesUpdate(BaseSchema):
    """Update user preferences."""
    
    email_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    job_notifications: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|system)$")
    default_format: Optional[str] = Field(None, pattern="^(json|csv|parquet|xml)$")


class AdminUserUpdate(BaseSchema):
    """Admin update user (can change role, status, etc.)."""
    
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = None
    status: Optional[str] = None
    email_verified: Optional[bool] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class UserPreferences(BaseSchema):
    """User preferences."""
    
    email_notifications: bool = True
    marketing_emails: bool = False
    job_notifications: bool = True
    weekly_digest: bool = True
    theme: str = "system"
    default_format: str = "json"


class UserResponse(BaseSchema, TimestampMixin):
    """User response schema."""
    
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    phone: Optional[str]
    timezone: str
    locale: str
    role: str
    status: str
    email_verified: bool
    
    @property
    def full_name(self) -> Optional[str]:
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.display_name


class UserDetailResponse(UserResponse):
    """Detailed user response with additional info."""
    
    preferences: Optional[UserPreferences] = None
    last_login_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    subscription_tier: str = "free"  # Default to free tier
    
    # Stats
    datasets_count: int = 0
    jobs_count: int = 0
    api_calls_count: int = 0


class UserListResponse(PaginatedResponse[UserResponse]):
    """Paginated list of users."""
    pass


class UserStatsResponse(BaseSchema):
    """User statistics."""
    
    total_datasets: int = 0
    total_rows_generated: int = 0
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    api_calls_this_month: int = 0
    storage_used_bytes: int = 0


class UserActivityItem(BaseSchema):
    """User activity item."""
    
    id: UUID
    action: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime


class UserActivityResponse(PaginatedResponse[UserActivityItem]):
    """User activity log."""
    pass


class PublicUserProfile(BaseSchema):
    """Public user profile (limited info)."""
    
    id: UUID
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
