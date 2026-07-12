"""
API Key service for Synthesize.io API.

Handles API key creation, validation, and management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateError,
    NotFoundError,
    AuthorizationError,
    RateLimitError,
)
from app.core.security import generate_api_key
from app.models import APIKey, APIRequestLog, User, Subscription
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyCreateResponse,
    APIKeyValidationResponse,
)


class APIKeyService:
    """Service for API key operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def create(
        self, data: APIKeyCreate, user_id: UUID, organization_id: Optional[UUID] = None
    ) -> tuple[APIKey, str]:
        """Create a new API key. Returns (api_key_model, plain_key)."""
        # Check API key limit
        self._check_api_key_limit(user_id)
        
        # Generate key - returns (prefix, full_key, key_hash)
        key_prefix, plain_key, key_hash = generate_api_key()
        
        # Create API key record
        api_key = APIKey(
            user_id=user_id,
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=data.scopes,
            expires_at=data.expires_at,
            rate_limit_per_minute=data.rate_limit,
            ip_whitelist=data.ip_whitelist,
            is_active=True,
            total_requests=0,
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key, plain_key
    
    def get_by_id(self, key_id: UUID) -> Optional[APIKey]:
        """Get API key by ID."""
        result = self.db.execute(
            select(APIKey).where(APIKey.id == key_id)
        )
        return result.scalar_one_or_none()
    
    def get_key(self, key_id: UUID, user_id: UUID = None) -> Optional[APIKey]:
        """Get API key by ID. Optionally with authorization check."""
        if user_id:
            try:
                return self.get_by_id_with_auth(key_id, user_id)
            except (NotFoundError, AuthorizationError):
                return None
        return self.get_by_id(key_id)
    
    def get_by_id_or_raise(self, key_id: UUID) -> APIKey:
        """Get API key by ID or raise NotFoundError."""
        api_key = self.get_by_id(key_id)
        if not api_key:
            raise NotFoundError("API Key", str(key_id))
        return api_key
    
    def get_by_id_with_auth(
        self, key_id: UUID, user_id: UUID
    ) -> APIKey:
        """Get API key with authorization check."""
        api_key = self.get_by_id_or_raise(key_id)
        
        if api_key.user_id != user_id:
            # Check organization membership
            if api_key.organization_id:
                from app.services.organization_service import OrganizationService
                org_service = OrganizationService(self.db)
                if not org_service.is_member(api_key.organization_id, user_id):
                    raise AuthorizationError("You don't have access to this API key")
            else:
                raise AuthorizationError("You don't have access to this API key")
        
        return api_key
    
    def update(
        self, key_id: UUID, data: APIKeyUpdate, user_id: UUID
    ) -> APIKey:
        """Update API key."""
        api_key = self.get_by_id_with_auth(key_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(api_key, field, value)
        
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key
    
    def delete(self, key_id: UUID, user_id: UUID) -> None:
        """Delete API key."""
        api_key = self.get_by_id_with_auth(key_id, user_id)
        self.db.delete(api_key)
        self.db.commit()
    
    def regenerate(
        self, key_id: UUID, user_id: UUID
    ) -> tuple[APIKey, str]:
        """Regenerate API key (creates new key, invalidates old)."""
        api_key = self.get_by_id_with_auth(key_id, user_id)
        
        # Generate new key - returns (prefix, full_key, key_hash)
        key_prefix, plain_key, key_hash = generate_api_key()
        
        # Update record
        api_key.key_hash = key_hash
        api_key.key_prefix = key_prefix
        api_key.total_requests = 0  # Reset usage count
        
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key, plain_key
    
    # =========================================================================
    # LISTING
    # =========================================================================
    
    def list_keys(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[APIKey], int]:
        """List user's API keys."""
        if organization_id:
            query = select(APIKey).where(APIKey.organization_id == organization_id)
            count_query = select(func.count(APIKey.id)).where(APIKey.organization_id == organization_id)
        else:
            query = select(APIKey).where(APIKey.user_id == user_id)
            count_query = select(func.count(APIKey.id)).where(APIKey.user_id == user_id)
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(APIKey.created_at.desc())
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        keys = list(result.scalars().all())
        
        return keys, total
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate_key(
        self,
        key: str,
        required_scopes: Optional[list[str]] = None,
        ip_address: Optional[str] = None,
    ) -> APIKeyValidationResponse:
        """Validate an API key and return user/org info."""
        if not key or len(key) < 8:
            return APIKeyValidationResponse(
                valid=False,
                error="Invalid API key format",
            )
        
        key_prefix = key[:8]
        key_hash = self._hash_key(key)
        
        # Find API key
        result = self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.key_prefix == key_prefix,
                    APIKey.key_hash == key_hash,
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return APIKeyValidationResponse(
                valid=False,
                error="API key not found",
            )
        
        # Check if active
        if not api_key.is_active:
            return APIKeyValidationResponse(
                valid=False,
                error="API key is deactivated",
            )
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return APIKeyValidationResponse(
                valid=False,
                error="API key has expired",
            )
        
        # Check IP whitelist
        if api_key.ip_whitelist and ip_address:
            if ip_address not in api_key.ip_whitelist:
                return APIKeyValidationResponse(
                    valid=False,
                    error="IP address not whitelisted",
                )
        
        # Check scopes
        if required_scopes:
            if not all(scope in api_key.scopes for scope in required_scopes):
                return APIKeyValidationResponse(
                    valid=False,
                    key_id=api_key.id,
                    error="Insufficient permissions",
                )
        
        # Check rate limit
        rate_limit_remaining = None
        rate_limit_reset = None
        if api_key.rate_limit_per_minute:
            remaining, reset = self._check_rate_limit(api_key)
            if remaining <= 0:
                return APIKeyValidationResponse(
                    valid=False,
                    key_id=api_key.id,
                    error="Rate limit exceeded",
                    rate_limit_remaining=0,
                    rate_limit_reset=reset,
                )
            rate_limit_remaining = remaining
            rate_limit_reset = reset
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        api_key.total_requests = (api_key.total_requests or 0) + 1
        self.db.commit()
        
        return APIKeyValidationResponse(
            valid=True,
            key_id=api_key.id,
            user_id=api_key.user_id,
            organization_id=api_key.organization_id,
            scopes=api_key.scopes,
            rate_limit_remaining=rate_limit_remaining,
            rate_limit_reset=rate_limit_reset,
        )
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    def log_usage(
        self,
        key_id: UUID,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
    ) -> None:
        """Log API key usage."""
        usage_log = APIRequestLog(
            api_key_id=key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow(),
        )
        self.db.add(usage_log)
        self.db.commit()
    
    def get_usage_stats(
        self,
        key_id: UUID,
        user_id: UUID,
        days: int = 30,
    ) -> dict:
        """Get API key usage statistics."""
        api_key = self.get_by_id_with_auth(key_id, user_id)
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get usage logs
        result = self.db.execute(
            select(APIRequestLog)
            .where(APIRequestLog.api_key_id == key_id)
            .where(APIRequestLog.timestamp >= since)
            .order_by(APIRequestLog.timestamp.desc())
            .limit(100)
        )
        logs = list(result.scalars().all())
        
        # Aggregate stats
        total_requests = len(logs)
        successful = len([l for l in logs if 200 <= l.status_code < 300])
        failed = len([l for l in logs if l.status_code >= 400])
        avg_response_time = (
            sum(l.response_time_ms for l in logs) / total_requests
            if total_requests > 0 else 0
        )
        
        # Group by endpoint
        by_endpoint = {}
        for log in logs:
            by_endpoint[log.endpoint] = by_endpoint.get(log.endpoint, 0) + 1
        
        # Group by status
        by_status = {}
        for log in logs:
            status_group = f"{log.status_code // 100}xx"
            by_status[status_group] = by_status.get(status_group, 0) + 1
        
        return {
            "key_id": key_id,
            "period_start": since,
            "period_end": datetime.utcnow(),
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "average_response_time_ms": avg_response_time,
            "requests_by_endpoint": by_endpoint,
            "requests_by_status": by_status,
            "recent_usage": [
                {
                    "timestamp": l.timestamp,
                    "endpoint": l.endpoint,
                    "method": l.method,
                    "status_code": l.status_code,
                    "response_time_ms": l.response_time_ms,
                }
                for l in logs[:10]
            ],
        }
    
    # =========================================================================
    # REVOKE & ROTATE OPERATIONS
    # =========================================================================
    
    def revoke(self, key_id: UUID, user_id: UUID) -> bool:
        """Revoke (deactivate) an API key."""
        try:
            api_key = self.get_by_id_with_auth(key_id, user_id)
            api_key.is_active = False
            api_key.revoked_at = datetime.utcnow()
            self.db.commit()
            return True
        except (NotFoundError, AuthorizationError):
            return False
    
    def revoke_all(self, user_id: UUID) -> int:
        """Revoke all active API keys for a user."""
        from datetime import datetime
        result = self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.user_id == user_id,
                    APIKey.is_active == True
                )
            )
        )
        keys = list(result.scalars().all())
        count = 0
        for key in keys:
            key.is_active = False
            key.revoked_at = datetime.utcnow()
            count += 1
        self.db.commit()
        return count
    
    def rotate(
        self, key_id: UUID, user_id: UUID, grace_period_hours: int = 0
    ) -> tuple[Optional[APIKey], str]:
        """Rotate an API key by creating a new one."""
        try:
            old_key = self.get_by_id_with_auth(key_id, user_id)
        except (NotFoundError, AuthorizationError):
            return None, ""
        
        # Create schema data for new key
        from app.schemas.api_key import APIKeyCreate
        data = APIKeyCreate(
            name=old_key.name,
            scopes=old_key.scopes or [],
            expires_at=old_key.expires_at,
        )
        new_key, plain_key = self.create(data, user_id)
        
        # Revoke old key after grace period (or immediately if 0)
        if grace_period_hours == 0:
            old_key.is_active = False
            old_key.revoked_at = datetime.utcnow()
        
        self.db.commit()
        return new_key, plain_key
    
    def get_user_usage_summary(self, user_id: UUID) -> dict:
        """Get aggregated usage summary for all user's API keys."""
        keys, _ = self.list_keys(user_id)
        
        return {
            "total_keys": len(keys),
            "active_keys": len([k for k in keys if k.is_active]),
            "requests_today": sum(k.total_requests or 0 for k in keys),
            "requests_this_month": sum(k.total_requests or 0 for k in keys),
            "most_active_key": keys[0].name if keys else None,
            "rate_limit_hits_today": 0,
        }
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _hash_key(self, key: str) -> str:
        """Hash API key for storage."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _check_api_key_limit(self, user_id: UUID) -> None:
        """Check if user has reached API key limit."""
        # Get subscription
        result = self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            from sqlalchemy.orm import selectinload
            sub_result = self.db.execute(
                select(Subscription)
                .options(selectinload(Subscription.plan))
                .where(Subscription.id == subscription.id)
            )
            subscription = sub_result.scalar_one()
            features = subscription.plan.features or {}
            max_keys = features.get("max_api_keys", 5)
        else:
            max_keys = 2  # Free tier
        
        # Count current keys
        count_result = self.db.execute(
            select(func.count(APIKey.id))
            .where(APIKey.user_id == user_id)
        )
        current_count = count_result.scalar() or 0
        
        if current_count >= max_keys:
            raise DuplicateError(
                "API Key",
                "limit",
                f"Maximum API key limit ({max_keys}) reached",
            )
    
    def _check_rate_limit(
        self, api_key: APIKey
    ) -> tuple[int, datetime]:
        """Check rate limit for API key. Returns (remaining, reset_time)."""
        if not api_key.rate_limit_per_minute:
            return -1, datetime.utcnow()
        
        # Get usage in current window (1 hour)
        window_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=1)
        
        count_result = self.db.execute(
            select(func.count(APIRequestLog.id))
            .where(APIRequestLog.api_key_id == api_key.id)
            .where(APIRequestLog.timestamp >= window_start)
        )
        used = count_result.scalar() or 0
        
        remaining = api_key.rate_limit_per_minute - used
        return remaining, window_end


# Import timedelta at the top
from datetime import timedelta


# Dependency injection helper
def get_api_key_service(db: Session) -> APIKeyService:
    """Get API key service instance."""
    return APIKeyService(db)
