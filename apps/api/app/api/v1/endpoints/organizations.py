"""
Organization endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
    Sorting,
)
from app.services.organization_service import OrganizationService
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationMemberResponse,
    OrganizationInviteCreate,
    OrganizationInviteResponse,
)
from app.schemas.base import MessageResponse

logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# ORGANIZATION CRUD
# =============================================================================

@router.post(
    "/",
    response_model=OrganizationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
def create_organization(
    data: OrganizationCreate,
    db: DBSession,
    user: CurrentUser,
):
    """Create a new organization."""
    org_service = OrganizationService(db)
    org = org_service.create(data, user.id)
    
    return OrganizationDetailResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website=org.website,
        billing_email=org.billing_email,
        settings=org.settings or {},
        created_at=org.created_at,
        updated_at=org.updated_at,
        member_count=1,  # Creator is first member
        owner_id=org.owner_id,
    )


@router.get(
    "/{org_id}",
    response_model=OrganizationDetailResponse,
    summary="Get organization",
)
def get_organization(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get organization details."""
    org_service = OrganizationService(db)
    org = org_service.get_by_id_or_raise(org_id)
    
    # Check membership
    is_member = org_service.is_member(org_id, user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    member_count = org_service.get_member_count(org_id)
    
    return OrganizationDetailResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website=org.website,
        billing_email=org.billing_email,
        settings=org.settings or {},
        created_at=org.created_at,
        updated_at=org.updated_at,
        member_count=member_count,
        owner_id=org.owner_id,
    )


@router.put(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
)
def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update organization. Requires admin role."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    role = org_service.get_member_role(org_id, user.id)
    if role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    org = org_service.update(org_id, data, user.id)
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


@router.delete(
    "/{org_id}",
    response_model=MessageResponse,
    summary="Delete organization",
)
def delete_organization(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Delete organization. Owner only."""
    org_service = OrganizationService(db)
    org = org_service.get_by_id_or_raise(org_id)
    
    if org.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete organization",
        )
    
    org_service.delete(org_id, user.id)
    return MessageResponse(message="Organization deleted successfully")


# =============================================================================
# MEMBERS
# =============================================================================

@router.get(
    "/{org_id}/members",
    response_model=List[OrganizationMemberResponse],
    summary="List organization members",
)
def list_members(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """List all members of an organization."""
    org_service = OrganizationService(db)
    
    # Check membership
    is_member = org_service.is_member(org_id, user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    members, total = org_service.get_members(
        org_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return [
        OrganizationMemberResponse(
            id=m.id,
            user_id=m.user_id,
            organization_id=org_id,
            email=m.user.email if m.user else "",
            first_name=m.user.first_name if m.user else None,
            last_name=m.user.last_name if m.user else None,
            display_name=f"{m.user.first_name or ''} {m.user.last_name or ''}".strip() if m.user else None,
            avatar_url=m.user.avatar_url if m.user else None,
            role=m.role,
            joined_at=m.created_at,
            invited_by=m.invited_by if hasattr(m, 'invited_by') else None,
        )
        for m in members
    ]


@router.put(
    "/{org_id}/members/{member_id}",
    response_model=OrganizationMemberResponse,
    summary="Update member role",
)
def update_member_role(
    org_id: UUID,
    member_id: UUID,
    role: str = Query(..., description="New role: owner, admin, member, viewer"),
    db: DBSession = None,
    user: CurrentUser = None,
):
    """Update a member's role. Admin or owner only."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    user_role = org_service.get_member_role(org_id, user.id)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    # Only owner can assign owner role
    if role == "owner" and user_role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can transfer ownership",
        )
    
    member = org_service.update_member_role(org_id, member_id, role, user.id)
    
    return OrganizationMemberResponse(
        id=member.id,
        user_id=member.user_id,
        organization_id=org_id,
        email=member.user.email if member.user else "",
        first_name=member.user.first_name if member.user else None,
        last_name=member.user.last_name if member.user else None,
        display_name=f"{member.user.first_name or ''} {member.user.last_name or ''}".strip() if member.user else None,
        avatar_url=member.user.avatar_url if member.user else None,
        role=member.role,
        joined_at=member.created_at,
        invited_by=member.invited_by if hasattr(member, 'invited_by') else None,
    )


@router.delete(
    "/{org_id}/members/{member_id}",
    response_model=MessageResponse,
    summary="Remove member",
)
def remove_member(
    org_id: UUID,
    member_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Remove a member from organization. Admin or owner only."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    user_role = org_service.get_member_role(org_id, user.id)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    org_service.remove_member(org_id, member_id, user.id)
    return MessageResponse(message="Member removed successfully")


@router.post(
    "/{org_id}/leave",
    response_model=MessageResponse,
    summary="Leave organization",
)
def leave_organization(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Leave an organization."""
    org_service = OrganizationService(db)
    org = org_service.get_by_id_or_raise(org_id)
    
    # Owner cannot leave
    if org.owner_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner cannot leave. Transfer ownership first.",
        )
    
    org_service.remove_member_by_user(org_id, user.id)
    return MessageResponse(message="Left organization successfully")


# =============================================================================
# INVITES
# =============================================================================

@router.get(
    "/{org_id}/invites",
    response_model=List[OrganizationInviteResponse],
    summary="List pending invites",
)
def list_invites(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """List pending invites for an organization."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    user_role = org_service.get_member_role(org_id, user.id)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    # Get organization for name
    org = org_service.get_by_id(org_id)
    org_name = org.name if org else ""
    
    invites, total = org_service.get_pending_invites(org_id)
    
    return [
        OrganizationInviteResponse(
            id=i.id,
            organization_id=org_id,
            organization_name=org_name,
            email=i.email,
            role=i.role,
            status=i.status if hasattr(i, 'status') else "pending",
            invited_by_id=i.invited_by,
            invited_by_name=None,  # Would require user lookup
            expires_at=i.expires_at,
            created_at=i.created_at,
        )
        for i in invites
    ]


@router.post(
    "/{org_id}/invites",
    response_model=OrganizationInviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create invite",
)
def create_invite(
    org_id: UUID,
    data: OrganizationInviteCreate,
    db: DBSession,
    user: CurrentUser,
):
    """Send an invitation to join organization."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    user_role = org_service.get_member_role(org_id, user.id)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    # Get organization for name
    org = org_service.get_by_id(org_id)
    org_name = org.name if org else ""
    
    invite = org_service.create_invite(
        org_id=org_id,
        email=data.email,
        role=data.role,
        invited_by=user.id,
    )
    
    return OrganizationInviteResponse(
        id=invite.id,
        organization_id=org_id,
        organization_name=org_name,
        email=invite.email,
        role=invite.role,
        status=invite.status if hasattr(invite, 'status') else "pending",
        invited_by_id=invite.invited_by_id,
        invited_by_name=None,
        expires_at=invite.expires_at,
        created_at=invite.created_at,
    )


@router.delete(
    "/{org_id}/invites/{invite_id}",
    response_model=MessageResponse,
    summary="Cancel invite",
)
def cancel_invite(
    org_id: UUID,
    invite_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Cancel a pending invite."""
    org_service = OrganizationService(db)
    
    # Check admin permission
    user_role = org_service.get_member_role(org_id, user.id)
    if user_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    org_service.cancel_invite(org_id, invite_id, user.id)
    return MessageResponse(message="Invite cancelled")


@router.post(
    "/invites/{invite_id}/accept",
    response_model=MessageResponse,
    summary="Accept invite",
)
def accept_invite(
    invite_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Accept an organization invitation."""
    org_service = OrganizationService(db)
    org_service.accept_invite(invite_id, user.id)
    return MessageResponse(message="Invitation accepted")


@router.post(
    "/invites/{invite_id}/decline",
    response_model=MessageResponse,
    summary="Decline invite",
)
def decline_invite(
    invite_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Decline an organization invitation."""
    org_service = OrganizationService(db)
    org_service.decline_invite(invite_id, user.email)
    return MessageResponse(message="Invitation declined")


# =============================================================================
# TEAM ACTIVITIES
# =============================================================================

@router.get(
    "/{org_id}/activities",
    summary="Get organization activity log",
)
async def get_organization_activities(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    user_filter: Optional[UUID] = Query(None, description="Filter by user ID"),
):
    """
    Get activity log for organization.
    
    Shows recent activities by team members including:
    - Dataset creation, updates, exports
    - Member additions and removals
    - Invite status changes
    - Settings changes
    """
    from app.services.activity_service import ActivityService, ActivityType
    
    org_service = OrganizationService(db)
    
    # Check membership
    if not org_service.is_member(org_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    # Parse activity type filter
    activity_types = None
    if activity_type:
        try:
            activity_types = [ActivityType(activity_type)]
        except ValueError:
            pass
    
    activity_service = ActivityService(db)
    activities, total = await activity_service.get_organization_activities(
        organization_id=org_id,
        activity_types=activity_types,
        user_id=user_filter,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return {
        "items": activities,
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }


@router.get(
    "/{org_id}/activities/summary",
    summary="Get activity summary statistics",
)
async def get_activity_summary(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
    days: int = Query(30, ge=1, le=365, description="Number of days to summarize"),
):
    """
    Get summarized activity statistics for organization.
    
    Returns:
    - Total activities count
    - Breakdown by activity type
    - Most active team members
    - Daily activity trend
    """
    from app.services.activity_service import ActivityService
    
    org_service = OrganizationService(db)
    
    # Only admins can view summary
    member = org_service.get_member(org_id, user.id)
    if not member or member.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view activity summary",
        )
    
    activity_service = ActivityService(db)
    summary = await activity_service.get_activity_summary(org_id, days=days)
    
    return summary


# =============================================================================
# TEAM USAGE & QUOTAS
# =============================================================================

@router.get(
    "/{org_id}/usage",
    summary="Get organization usage statistics",
)
def get_organization_usage(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """
    Get aggregated usage statistics for organization.
    
    Combines usage from all team members.
    """
    from app.services.activity_service import TeamQuotaService
    
    org_service = OrganizationService(db)
    
    # Check membership
    if not org_service.is_member(org_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    quota_service = TeamQuotaService(db)
    usage = quota_service.get_organization_usage(org_id)
    
    # Get organization plan limits
    org = org_service.get_by_id(org_id)
    plan_limits = quota_service._get_plan_limits(org.plan if org else "free")
    
    return {
        "usage": usage,
        "limits": plan_limits,
        "plan": org.plan if org else "free",
    }


@router.get(
    "/{org_id}/quota/check",
    summary="Check organization quota availability",
)
def check_organization_quota(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
    quota_type: str = Query(..., description="Quota type: datasets, rows, storage"),
    amount: int = Query(1, ge=1, description="Amount to check"),
):
    """
    Check if organization has enough quota for an operation.
    
    Useful before starting a large generation job.
    """
    from app.services.activity_service import TeamQuotaService
    
    org_service = OrganizationService(db)
    
    if not org_service.is_member(org_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    quota_service = TeamQuotaService(db)
    is_allowed, message = quota_service.check_organization_quota(
        org_id, quota_type, amount
    )
    
    return {
        "allowed": is_allowed,
        "message": message,
        "quota_type": quota_type,
        "requested_amount": amount,
    }


# =============================================================================
# SHARED DATASETS
# =============================================================================

@router.post(
    "/{org_id}/datasets/{dataset_id}/share",
    summary="Share dataset with organization",
)
def share_dataset_with_org(
    org_id: UUID,
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
    access_level: str = Query("view", description="Access level: view, edit, admin"),
):
    """
    Share a dataset with the organization.
    
    Access levels:
    - **view**: Members can view and export
    - **edit**: Members can modify schema and regenerate
    - **admin**: Members can delete and manage sharing
    """
    from app.services.activity_service import DatasetAccessService, ActivityService, ActivityType
    
    org_service = OrganizationService(db)
    
    # Verify membership
    if not org_service.is_member(org_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    access_service = DatasetAccessService(db)
    
    try:
        access_service.share_dataset_with_org(
            dataset_id=dataset_id,
            organization_id=org_id,
            user_id=user.id,
            access_level=access_level,
        )
        
        # Log activity
        activity_service = ActivityService(db)
        activity_service.log_activity_sync(
            activity_type=ActivityType.DATASET_SHARED,
            user_id=user.id,
            organization_id=org_id,
            resource_type="dataset",
            resource_id=dataset_id,
            metadata={"access_level": access_level},
        )
        
        return MessageResponse(message="Dataset shared with organization")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{org_id}/datasets/{dataset_id}/share",
    summary="Remove dataset from organization sharing",
)
def unshare_dataset(
    org_id: UUID,
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Remove dataset from organization sharing."""
    from app.services.activity_service import DatasetAccessService, ActivityService, ActivityType
    
    access_service = DatasetAccessService(db)
    
    try:
        access_service.unshare_dataset(dataset_id, user.id)
        
        # Log activity
        activity_service = ActivityService(db)
        activity_service.log_activity_sync(
            activity_type=ActivityType.DATASET_UNSHARED,
            user_id=user.id,
            organization_id=org_id,
            resource_type="dataset",
            resource_id=dataset_id,
        )
        
        return MessageResponse(message="Dataset removed from organization")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# =============================================================================
# ORGANIZATION DATASETS
# =============================================================================

@router.get(
    "/{org_id}/datasets",
    summary="List organization datasets",
)
def list_org_datasets(
    org_id: UUID,
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """List datasets shared with organization."""
    org_service = OrganizationService(db)
    
    # Check membership
    is_member = org_service.is_member(org_id, user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    from app.services.dataset_service import DatasetService
    dataset_service = DatasetService(db)
    datasets, total = dataset_service.list_datasets(
        user_id=user.id,
        organization_id=org_id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return {
        "items": [
            {
                "id": str(d.id),
                "name": d.name,
                "description": d.description,
                "category": d.category,
                "output_format": d.output_format,
                "fields_count": len(d.schema_fields) if d.schema_fields else 0,
                "created_at": d.created_at.isoformat(),
            }
            for d in datasets
        ],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }

