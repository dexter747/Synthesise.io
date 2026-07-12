"""
API key management endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
)
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyDetailResponse,
    APIKeyCreatedResponse,
    APIKeyUsageResponse,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# API KEY CRUD
# =============================================================================

@router.get(
    "/",
    response_model=List[APIKeyResponse],
    summary="List API keys",
)
def list_api_keys(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    include_revoked: bool = Query(False, description="Include revoked keys"),
):
    """List current user's API keys."""
    api_key_service = APIKeyService(db)
    keys, total = api_key_service.list_keys(
        user_id=user.id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    # Filter out revoked keys if not including them
    if not include_revoked:
        keys = [k for k in keys if k.is_active]
    
    return [
        APIKeyResponse(
            id=k.id,
            user_id=k.user_id,
            name=k.name,
            key_prefix=k.key_prefix,
            scopes=k.scopes or [],
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
            created_at=k.created_at,
            usage_count=k.total_requests or 0,
        )
        for k in keys
    ]


@router.post(
    "/",
    response_model=APIKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
)
def create_api_key(
    data: APIKeyCreate,
    db: DBSession,
    user: CurrentUser,
):
    """
    Create a new API key.
    
    **Important:** The full API key is only shown once at creation time.
    Store it securely as it cannot be retrieved later.
    """
    api_key_service = APIKeyService(db)
    key, plain_key = api_key_service.create(
        data=data,
        user_id=user.id,
    )
    
    return APIKeyCreatedResponse(
        id=key.id,
        name=key.name,
        key=plain_key,  # Full key - only shown once!
        key_prefix=key.key_prefix,
        scopes=key.scopes or [],
        expires_at=key.expires_at,
        created_at=key.created_at,
    )


# =============================================================================
# SCOPES REFERENCE (must be before /{key_id} routes)
# =============================================================================

@router.get(
    "/scopes",
    summary="List available scopes",
)
def list_available_scopes():
    """List all available API key scopes with descriptions."""
    return {
        "scopes": [
            {"name": "datasets:read", "description": "Read access to datasets"},
            {"name": "datasets:write", "description": "Create, update, and delete datasets"},
            {"name": "generation:read", "description": "Read access to generation jobs"},
            {"name": "generation:write", "description": "Create and manage generation jobs"},
            {"name": "generation:download", "description": "Download generated files"},
            {"name": "user:read", "description": "Read user profile information"},
            {"name": "billing:read", "description": "Read billing and usage information"},
            {"name": "webhooks:manage", "description": "Manage webhook configurations"},
        ]
    }


@router.get(
    "/{key_id}",
    response_model=APIKeyDetailResponse,
    summary="Get API key details",
)
def get_api_key(
    key_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get detailed information about an API key."""
    api_key_service = APIKeyService(db)
    key = api_key_service.get_key(key_id, user.id)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return APIKeyDetailResponse(
        id=key.id,
        user_id=key.user_id,
        name=key.name,
        key_prefix=key.key_prefix,
        scopes=key.scopes or [],
        is_active=key.is_active,
        last_used_at=key.last_used_at,
        expires_at=key.expires_at,
        created_at=key.created_at,
        updated_at=key.updated_at,
        usage_count=key.total_requests or 0,
        rate_limit=key.rate_limit_per_minute,
    )


@router.put(
    "/{key_id}",
    response_model=APIKeyResponse,
    summary="Update API key",
)
def update_api_key(
    key_id: UUID,
    data: APIKeyUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update API key name or scopes."""
    api_key_service = APIKeyService(db)
    key = api_key_service.update(key_id, data, user.id)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return APIKeyResponse(
        id=key.id,
        user_id=key.user_id,
        name=key.name,
        key_prefix=key.key_prefix,
        scopes=key.scopes or [],
        is_active=key.is_active,
        last_used_at=key.last_used_at,
        expires_at=key.expires_at,
        created_at=key.created_at,
        usage_count=key.total_requests or 0,
    )


@router.delete(
    "/{key_id}",
    response_model=MessageResponse,
    summary="Revoke API key",
)
def revoke_api_key(
    key_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Revoke (deactivate) an API key. This cannot be undone."""
    api_key_service = APIKeyService(db)
    success = api_key_service.revoke(key_id, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return MessageResponse(message="API key revoked successfully")


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post(
    "/revoke-all",
    response_model=MessageResponse,
    summary="Revoke all API keys",
)
def revoke_all_api_keys(
    db: DBSession,
    user: CurrentUser,
):
    """Revoke all active API keys for current user."""
    api_key_service = APIKeyService(db)
    count = api_key_service.revoke_all(user.id)
    return MessageResponse(message=f"Revoked {count} API keys")


# =============================================================================
# USAGE & STATS
# =============================================================================

@router.get(
    "/{key_id}/usage",
    response_model=APIKeyUsageResponse,
    summary="Get API key usage",
)
def get_api_key_usage(
    key_id: UUID,
    db: DBSession,
    user: CurrentUser,
    period: str = Query("30d", description="Period: 7d, 30d, 90d"),
):
    """Get usage statistics for an API key."""
    api_key_service = APIKeyService(db)
    
    # Verify ownership
    key = api_key_service.get_key(key_id, user.id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    usage = api_key_service.get_usage_stats(key_id, period)
    
    return APIKeyUsageResponse(
        key_id=key_id,
        period=period,
        total_requests=usage.get("total_requests", 0),
        successful_requests=usage.get("successful_requests", 0),
        failed_requests=usage.get("failed_requests", 0),
        rate_limited_requests=usage.get("rate_limited_requests", 0),
        requests_by_endpoint=usage.get("requests_by_endpoint", {}),
        requests_by_day=usage.get("requests_by_day", []),
    )


@router.get(
    "/usage/summary",
    summary="Get usage summary",
)
def get_usage_summary(
    db: DBSession,
    user: CurrentUser,
):
    """Get aggregated usage summary across all API keys."""
    api_key_service = APIKeyService(db)
    summary = api_key_service.get_user_usage_summary(user.id)
    
    return {
        "total_keys": summary.get("total_keys", 0),
        "active_keys": summary.get("active_keys", 0),
        "total_requests_today": summary.get("requests_today", 0),
        "total_requests_this_month": summary.get("requests_this_month", 0),
        "most_active_key": summary.get("most_active_key"),
        "rate_limit_hits_today": summary.get("rate_limit_hits_today", 0),
    }


# =============================================================================
# ROTATION
# =============================================================================

@router.post(
    "/{key_id}/rotate",
    response_model=APIKeyCreatedResponse,
    summary="Rotate API key",
)
def rotate_api_key(
    key_id: UUID,
    db: DBSession,
    user: CurrentUser,
    keep_old_active_hours: int = Query(
        0,
        ge=0,
        le=72,
        description="Hours to keep old key active (0-72)",
    ),
):
    """
    Rotate an API key by creating a new one and optionally keeping the old
    one active for a grace period.
    
    Returns the new key. Store it securely as it cannot be retrieved later.
    """
    api_key_service = APIKeyService(db)
    new_key, plain_key = api_key_service.rotate(
        key_id=key_id,
        user_id=user.id,
        grace_period_hours=keep_old_active_hours,
    )
    
    if not new_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return APIKeyCreatedResponse(
        id=new_key.id,
        name=new_key.name,
        key=plain_key,
        key_prefix=new_key.key_prefix,
        scopes=new_key.scopes or [],
        expires_at=new_key.expires_at,
        created_at=new_key.created_at,
    )
