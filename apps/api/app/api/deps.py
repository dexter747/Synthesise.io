"""
API Dependencies for Synthesize.io.

This module provides FastAPI dependencies for authentication,
authorization, database sessions, and other common operations.
"""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_access_token
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
)
from app.models import User, Subscription, APIKey
from app.services.api_key_service import APIKeyService


# =============================================================================
# SECURITY SCHEMES
# =============================================================================

# Bearer token authentication
bearer_scheme = HTTPBearer(auto_error=False)


# =============================================================================
# DATABASE DEPENDENCY
# =============================================================================

# Type alias for database session dependency
DBSession = Annotated[Session, Depends(get_db)]


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

def get_current_user_optional(
    db: DBSession,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)] = None,
    x_api_key: Annotated[Optional[str], Header()] = None,
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Supports both JWT and API key authentication.
    """
    user = None
    
    # Try JWT authentication first
    if credentials:
        user_id = verify_access_token(credentials.credentials)
        if user_id:
            result = db.execute(
                select(User).where(User.id == UUID(user_id))
            )
            user = result.scalar_one_or_none()
    
    # Try API key authentication if no JWT
    if not user and x_api_key:
        api_key_service = APIKeyService(db)
        validation = api_key_service.validate_key(x_api_key)
        if validation.valid and validation.user_id:
            result = db.execute(
                select(User).where(User.id == validation.user_id)
            )
            user = result.scalar_one_or_none()
    
    return user


def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_user_optional)],
) -> User:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check user status
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended",
        )
    
    if user.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
        )
    
    return user


def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user (email verified optional).
    """
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    return user


def get_current_verified_user(
    user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current user with verified email.
    """
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    return user


# Type aliases for user dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]


# =============================================================================
# ROLE-BASED AUTHORIZATION
# =============================================================================

class RoleChecker:
    """Dependency to check user role."""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(
        self, user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


# Role checker instances
require_admin = RoleChecker(["admin", "super_admin"])
require_super_admin = RoleChecker(["super_admin"])

# Type aliases for role-based dependencies
AdminUser = Annotated[User, Depends(require_admin)]
SuperAdminUser = Annotated[User, Depends(require_super_admin)]


# =============================================================================
# SUBSCRIPTION DEPENDENCIES
# =============================================================================

def get_user_subscription(
    db: DBSession,
    user: CurrentUser,
) -> Optional[Subscription]:
    """Get user's active subscription."""
    from sqlalchemy.orm import selectinload
    
    result = db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.user_id == user.id)
        .where(Subscription.status.in_(["active", "trialing", "past_due"]))
        .order_by(Subscription.created_at.desc())
    )
    return result.scalars().first()


def require_subscription(
    subscription: Annotated[Optional[Subscription], Depends(get_user_subscription)],
) -> Subscription:
    """Require user to have an active subscription."""
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required",
        )
    return subscription


def require_paid_subscription(
    subscription: Annotated[Subscription, Depends(require_subscription)],
) -> Subscription:
    """Require user to have a paid (non-free) subscription."""
    if subscription.plan.slug == "free":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Paid subscription required for this feature",
        )
    return subscription


# Type aliases
UserSubscription = Annotated[Optional[Subscription], Depends(get_user_subscription)]
RequiredSubscription = Annotated[Subscription, Depends(require_subscription)]
PaidSubscription = Annotated[Subscription, Depends(require_paid_subscription)]


# =============================================================================
# API KEY DEPENDENCIES
# =============================================================================

def get_api_key(
    db: DBSession,
    x_api_key: Annotated[Optional[str], Header()] = None,
    request: Request = None,
) -> Optional[APIKey]:
    """Get and validate API key from header."""
    if not x_api_key:
        return None
    
    api_key_service = APIKeyService(db)
    ip_address = request.client.host if request and request.client else None
    
    validation = api_key_service.validate_key(
        key=x_api_key,
        ip_address=ip_address,
    )
    
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=validation.error or "Invalid API key",
        )
    
    result = db.execute(
        select(APIKey).where(APIKey.id == validation.key_id)
    )
    return result.scalar_one_or_none()


def require_api_key(
    api_key: Annotated[Optional[APIKey], Depends(get_api_key)],
) -> APIKey:
    """Require valid API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )
    return api_key


def require_api_scopes(required_scopes: list[str]):
    """Create dependency to require specific API key scopes."""
    
    def check_scopes(
        api_key: Annotated[APIKey, Depends(require_api_key)],
    ) -> APIKey:
        if not all(scope in api_key.scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scopes: {', '.join(required_scopes)}",
            )
        return api_key
    
    return check_scopes


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self._requests: dict[str, list[datetime]] = {}
    
    def __call__(
        self,
        request: Request,
        user: OptionalUser = None,
    ) -> None:
        # Get identifier
        if user:
            identifier = f"user:{user.id}"
        else:
            identifier = f"ip:{request.client.host if request.client else 'unknown'}"
        
        now = datetime.utcnow()
        
        # Initialize or get request history
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Clean old requests
        minute_ago = now.timestamp() - 60
        hour_ago = now.timestamp() - 3600
        
        self._requests[identifier] = [
            ts for ts in self._requests[identifier]
            if ts.timestamp() > hour_ago
        ]
        
        # Count requests
        recent_minute = len([
            ts for ts in self._requests[identifier]
            if ts.timestamp() > minute_ago
        ])
        recent_hour = len(self._requests[identifier])
        
        # Check limits
        if recent_minute >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per minute)",
                headers={"Retry-After": "60"},
            )
        
        if recent_hour >= self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per hour)",
                headers={"Retry-After": "3600"},
            )
        
        # Record request
        self._requests[identifier].append(now)


# Rate limiter instances
default_rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
strict_rate_limiter = RateLimiter(requests_per_minute=10, requests_per_hour=100)
generous_rate_limiter = RateLimiter(requests_per_minute=120, requests_per_hour=5000)


def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
) -> list:
    """
    Create a rate limiting dependency for endpoints.
    
    Usage:
        @router.post("/endpoint", dependencies=[rate_limit(requests_per_minute=10)])
    """
    limiter = RateLimiter(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
    )
    return [Depends(limiter)]


# =============================================================================
# PAGINATION
# =============================================================================

class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
    ):
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 1
        if per_page > 100:
            per_page = 100
        
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


Pagination = Annotated[PaginationParams, Depends()]


# =============================================================================
# COMMON FILTERS
# =============================================================================

class SortParams:
    """Common sorting parameters."""
    
    def __init__(
        self,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"


Sorting = Annotated[SortParams, Depends()]


# =============================================================================
# QUOTA ENFORCEMENT DEPENDENCIES
# =============================================================================

class QuotaChecker:
    """Dependency to check user quotas before operations."""
    
    def __init__(self, usage_type: str, amount: int = 1):
        self.usage_type = usage_type
        self.amount = amount
    
    def __call__(
        self,
        db: DBSession,
        user: CurrentUser,
    ) -> User:
        from app.services.usage_service import UsageService, UsageQuotaExceeded
        
        service = UsageService(db)
        try:
            service.check_quota(
                user.id,
                self.usage_type,
                self.amount,
                raise_exception=True
            )
        except UsageQuotaExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": f"Quota exceeded for {e.usage_type}",
                    "usage_type": e.usage_type,
                    "limit": e.limit,
                    "current": e.current,
                    "upgrade_url": "/pricing"
                }
            )
        return user


class RowQuotaChecker:
    """Check if user can generate specified number of rows."""
    
    def __init__(self, row_count_param: str = "row_count"):
        self.row_count_param = row_count_param
    
    def __call__(
        self,
        db: DBSession,
        user: CurrentUser,
        request: Request,
    ) -> User:
        from app.services.usage_service import UsageService, UsageQuotaExceeded
        
        # Try to get row_count from request body or query params
        row_count = None
        
        # This would need async handling for body
        # For now, this is used as a general job creation check
        service = UsageService(db)
        try:
            service.check_job_quota(user.id)
        except UsageQuotaExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": f"Quota exceeded: {e.usage_type}",
                    "usage_type": e.usage_type,
                    "limit": e.limit,
                    "current": e.current,
                    "upgrade_url": "/pricing"
                }
            )
        return user


def check_job_creation_quota(
    db: DBSession,
    user: CurrentUser,
) -> User:
    """Check if user can create a new generation job."""
    from app.services.usage_service import UsageService, UsageQuotaExceeded
    
    service = UsageService(db)
    try:
        service.check_job_quota(user.id)
    except UsageQuotaExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"Job creation limit reached",
                "usage_type": e.usage_type,
                "limit": e.limit,
                "current": e.current,
                "upgrade_url": "/pricing"
            }
        )
    return user


def check_api_call_quota(
    db: DBSession,
    user: CurrentUser,
) -> User:
    """Check and increment API call quota."""
    from app.services.usage_service import UsageService, UsageQuotaExceeded
    
    service = UsageService(db)
    
    # Check quota first
    try:
        service.check_quota(user.id, "api_calls_per_month", 1, raise_exception=True)
    except UsageQuotaExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "API call limit exceeded",
                "usage_type": e.usage_type,
                "limit": e.limit,
                "current": e.current,
                "upgrade_url": "/pricing"
            }
        )
    
    # Increment the counter
    service.increment_api_calls(user.id)
    return user


# Quota checker instances
require_job_quota = QuotaChecker("jobs_per_month", 1)
require_api_quota = Depends(check_api_call_quota)

# Type aliases for quota dependencies
JobQuotaUser = Annotated[User, Depends(check_job_creation_quota)]
APIQuotaUser = Annotated[User, Depends(check_api_call_quota)]


# =============================================================================
# REQUEST CONTEXT
# =============================================================================

class RequestContext:
    """Request context with common information."""
    
    def __init__(
        self,
        request: Request,
        user: OptionalUser = None,
    ):
        self.request = request
        self.user = user
        self.ip_address = request.client.host if request.client else None
        self.user_agent = request.headers.get("user-agent")
        self.request_id = request.headers.get("x-request-id")


Context = Annotated[RequestContext, Depends()]
