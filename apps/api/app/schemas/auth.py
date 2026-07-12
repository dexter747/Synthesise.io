"""
Authentication schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import BaseSchema


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class RegisterRequest(BaseSchema):
    """User registration request."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseSchema):
    """User login request."""
    
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class RefreshTokenRequest(BaseSchema):
    """Token refresh request."""
    
    refresh_token: str


class ForgotPasswordRequest(BaseSchema):
    """Forgot password request."""
    
    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    """Password reset request."""
    
    token: str
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class ChangePasswordRequest(BaseSchema):
    """Change password request."""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class VerifyEmailRequest(BaseSchema):
    """Email verification request."""
    
    token: str


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class TokenResponse(BaseSchema):
    """JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class AuthUserResponse(BaseSchema):
    """Authenticated user response (minimal info returned on login)."""
    
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    email_verified: bool
    role: str
    status: str


class LoginResponse(BaseSchema):
    """Login response with token and user info."""
    
    token: TokenResponse
    user: AuthUserResponse


class RegisterResponse(BaseSchema):
    """Registration response."""
    
    message: str
    user: AuthUserResponse
    token: TokenResponse


class SessionInfo(BaseSchema):
    """User session information."""
    
    id: UUID
    device_info: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_current: bool = False


class SessionListResponse(BaseSchema):
    """List of user sessions."""
    
    sessions: list[SessionInfo]
    total: int
