"""
User endpoints for Synthesize.io API.
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import (
    DBSession,
    CurrentUser,
    AdminUser,
    Pagination,
    Sorting,
    UserSubscription,
)
from app.services.user_service import UserService
from app.services.organization_service import OrganizationService
from app.schemas.user import (
    UserUpdate,
    UserPreferencesUpdate,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
    UserStatsResponse,
    UserActivityResponse,
    UserPreferences,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# CURRENT USER PROFILE
# =============================================================================

@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get current user profile",
)
def get_current_user_profile(
    db: DBSession,
    user: CurrentUser,
    subscription: UserSubscription,
):
    """Get current authenticated user's full profile."""
    user_service = UserService(db)
    stats = user_service.get_stats(user.id)
    
    # Determine subscription tier from active subscription
    subscription_tier = "free"
    if subscription and subscription.plan:
        subscription_tier = subscription.plan.tier.value
    
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        phone=user.phone,
        timezone=user.timezone or "UTC",
        locale=user.locale or "en",
        role=user.role,
        status=user.status,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        preferences=UserPreferences(**(user.preferences or {})),
        last_login_at=user.last_login_at,
        two_factor_enabled=user.two_factor_enabled or False,
        subscription_tier=subscription_tier,
        datasets_count=stats.get("total_datasets", 0),
        jobs_count=stats.get("total_jobs", 0),
        api_calls_count=stats.get("api_calls_this_month", 0),
    )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_current_user(
    data: UserUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update current user's profile."""
    user_service = UserService(db)
    updated_user = user_service.update(user.id, data)
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        display_name=updated_user.display_name,
        avatar_url=updated_user.avatar_url,
        phone=updated_user.phone,
        timezone=updated_user.timezone or "UTC",
        locale=updated_user.locale or "en",
        role=updated_user.role,
        status=updated_user.status,
        email_verified=updated_user.email_verified,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.put(
    "/me/preferences",
    response_model=UserPreferences,
    summary="Update user preferences",
)
def update_user_preferences(
    data: UserPreferencesUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update current user's preferences."""
    user_service = UserService(db)
    updated_user = user_service.update_preferences(user.id, data)
    return UserPreferences(**(updated_user.preferences or {}))


@router.post(
    "/update-location",
    response_model=MessageResponse,
    summary="Update user location data",
)
def update_user_location(
    db: DBSession,
    user: CurrentUser,
    ip_address: str = None,
    country: str = None,
    city: str = None,
    region: str = None,
):
    """Update user's location information based on IP."""
    # This is a simple endpoint to track user location
    # You could store this in user preferences or a separate table
    user_service = UserService(db)
    
    location_data = {
        "last_ip": ip_address,
        "last_country": country,
        "last_city": city,
        "last_region": region,
    }
    
    # Update user preferences with location data
    current_prefs = user.preferences or {}
    current_prefs.update(location_data)
    
    from app.schemas.user import UserPreferencesUpdate
    user_service.update_preferences(user.id, UserPreferencesUpdate(preferences=current_prefs))
    
    return MessageResponse(message="Location updated successfully")


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete current user account",
)
def delete_current_user(
    db: DBSession,
    user: CurrentUser,
):
    """Delete current user's account (soft delete)."""
    user_service = UserService(db)
    user_service.delete(user.id)
    return MessageResponse(message="Account deleted successfully")


# =============================================================================
# USER STATS & ACTIVITY
# =============================================================================

@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Get current user stats",
)
def get_current_user_stats(
    db: DBSession,
    user: CurrentUser,
):
    """Get current user's statistics."""
    user_service = UserService(db)
    stats = user_service.get_stats(user.id)
    return UserStatsResponse(**stats)


@router.get(
    "/me/activity",
    response_model=UserActivityResponse,
    summary="Get user activity log",
)
def get_current_user_activity(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """Get current user's activity log."""
    user_service = UserService(db)
    activities = user_service.get_activity(
        user.id,
        limit=pagination.per_page,
        offset=pagination.offset,
    )
    
    return UserActivityResponse(
        items=[
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "details": a.new_values,
                "ip_address": a.ip_address,
                "created_at": a.created_at,
            }
            for a in activities
        ],
        total=len(activities),  # TODO: Get actual total
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=1,  # TODO: Calculate
        has_next=False,  # TODO: Calculate based on actual total
        has_prev=pagination.page > 1,
    )


# =============================================================================
# USER ORGANIZATIONS
# =============================================================================

@router.get(
    "/me/organizations",
    summary="Get user's organizations",
)
def get_user_organizations(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """Get organizations the current user belongs to."""
    org_service = OrganizationService(db)
    orgs, total = org_service.get_user_organizations(
        user.id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return {
        "items": [
            {
                "id": str(o.id),
                "name": o.name,
                "slug": o.slug,
                "logo_url": o.logo_url,
                "role": "member",  # TODO: Get actual role
            }
            for o in orgs
        ],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }


# =============================================================================
# USER INVITES
# =============================================================================

@router.get(
    "/me/invites",
    summary="Get pending organization invites",
)
def get_user_invites(
    db: DBSession,
    user: CurrentUser,
):
    """Get pending organization invites for current user."""
    org_service = OrganizationService(db)
    invites = org_service.get_user_pending_invites(user.email)
    
    return {
        "items": [
            {
                "id": str(i.id),
                "organization_id": str(i.organization_id),
                "organization_name": i.organization.name if i.organization else None,
                "role": i.role,
                "expires_at": i.expires_at.isoformat() if i.expires_at else None,
            }
            for i in invites
        ],
        "total": len(invites),
    }


# =============================================================================
# ADMIN: USER MANAGEMENT
# =============================================================================

@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users (admin)",
)
def list_users(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    sorting: Sorting,
    search: str = None,
    role: str = None,
    status: str = None,
):
    """List all users. Admin only."""
    user_service = UserService(db)
    users, total = user_service.list_users(
        page=pagination.page,
        per_page=pagination.per_page,
        search=search,
        role=role,
        status=status,
        sort_by=sorting.sort_by,
        sort_order=sorting.sort_order,
    )
    
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    return UserListResponse(
        items=[
            UserResponse(
                id=u.id,
                email=u.email,
                first_name=u.first_name,
                last_name=u.last_name,
                display_name=u.display_name,
                avatar_url=u.avatar_url,
                phone=u.phone,
                timezone=u.timezone or "UTC",
                locale=u.locale or "en",
                role=u.role,
                status=u.status,
                email_verified=u.email_verified,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1,
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user by ID (admin)",
)
def get_user(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """Get user by ID. Admin only."""
    user_service = UserService(db)
    user = user_service.get_by_id_or_raise(user_id)
    stats = user_service.get_stats(user_id)
    
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        phone=user.phone,
        timezone=user.timezone or "UTC",
        locale=user.locale or "en",
        role=user.role,
        status=user.status,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        two_factor_enabled=user.two_factor_enabled or False,
        datasets_count=stats.get("total_datasets", 0),
        jobs_count=stats.get("total_jobs", 0),
    )
