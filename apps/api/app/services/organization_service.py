"""
Organization service for Synthesize.io API.

Handles organization CRUD, member management, and org-level operations.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DuplicateError,
    NotFoundError,
    ValidationError,
    AuthorizationError,
)
from app.models import Organization, OrganizationMember, OrganizationInvitation, User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationSettingsUpdate,
)
from app.utils.helpers import generate_slug


class OrganizationService:
    """Service for organization operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # =========================================================================
    # ORGANIZATION CRUD
    # =========================================================================
    
    def create(
        self, data: OrganizationCreate, owner_id: UUID
    ) -> Organization:
        """Create a new organization."""
        # Generate slug if not provided
        if data.slug:
            # Check if slug is unique
            existing = self._get_by_slug(data.slug)
            if existing:
                raise DuplicateError("Organization", "slug", data.slug)
            slug = data.slug
        else:
            slug = self._generate_unique_slug(data.name)
        
        # Create organization
        org = Organization(
            name=data.name,
            slug=slug,
            description=data.description,
            website=str(data.website) if data.website else None,
            industry=data.industry,
            size=data.size,
            owner_id=owner_id,
            plan="free",
            status="active",
        )
        
        self.db.add(org)
        self.db.flush()
        
        # Add owner as admin member
        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_id,
            role="admin",
        )
        self.db.add(member)
        
        self.db.commit()
        self.db.refresh(org)
        
        return org
    
    def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        """Get organization by ID."""
        result = self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()
    
    def get_by_id_or_raise(self, org_id: UUID) -> Organization:
        """Get organization by ID or raise NotFoundError."""
        org = self.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization", str(org_id))
        return org
    
    def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        return self._get_by_slug(slug)
    
    def update(
        self, org_id: UUID, data: OrganizationUpdate, user_id: UUID
    ) -> Organization:
        """Update organization."""
        org = self.get_by_id_or_raise(org_id)
        
        # Check permissions
        self._check_admin_permission(org_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "website" and value:
                value = str(value)
            setattr(org, field, value)
        
        self.db.commit()
        self.db.refresh(org)
        
        return org
    
    def update_settings(
        self, org_id: UUID, data: OrganizationSettingsUpdate, user_id: UUID
    ) -> Organization:
        """Update organization settings."""
        org = self.get_by_id_or_raise(org_id)
        
        # Check permissions
        self._check_admin_permission(org_id, user_id)
        
        settings = org.settings or {}
        update_data = data.model_dump(exclude_unset=True)
        settings.update(update_data)
        
        org.settings = settings
        self.db.commit()
        self.db.refresh(org)
        
        return org
    
    def delete(self, org_id: UUID, user_id: UUID) -> None:
        """Delete organization (soft delete)."""
        org = self.get_by_id_or_raise(org_id)
        
        # Only owner can delete
        if org.owner_id != user_id:
            raise AuthorizationError("Only the owner can delete the organization")
        
        org.status = "deleted"
        org.deleted_at = datetime.utcnow()
        self.db.commit()
    
    # =========================================================================
    # MEMBER MANAGEMENT
    # =========================================================================
    
    def get_members(
        self, org_id: UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[OrganizationMember], int]:
        """Get organization members."""
        query = (
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == org_id)
            .order_by(OrganizationMember.created_at)
        )
        
        count_query = (
            select(func.count(OrganizationMember.id))
            .where(OrganizationMember.organization_id == org_id)
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        members = list(result.scalars().all())
        
        return members, total
    
    def get_member_count(self, org_id: UUID) -> int:
        """Get the number of members in an organization."""
        result = self.db.execute(
            select(func.count(OrganizationMember.id))
            .where(OrganizationMember.organization_id == org_id)
        )
        return result.scalar() or 0
    
    def get_member(
        self, org_id: UUID, user_id: UUID
    ) -> Optional[OrganizationMember]:
        """Get specific organization member."""
        result = self.db.execute(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    def add_member(
        self,
        org_id: UUID,
        user_id: UUID,
        role: str,
        added_by: UUID,
    ) -> OrganizationMember:
        """Add a member to organization."""
        # Check if already a member
        existing = self.get_member(org_id, user_id)
        if existing:
            raise DuplicateError("Member", "user_id", str(user_id))
        
        # Check permissions
        self._check_admin_permission(org_id, added_by)
        
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=added_by,
        )
        
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        
        return member
    
    def update_member_role(
        self,
        org_id: UUID,
        user_id: UUID,
        role: str,
        updated_by: UUID,
    ) -> OrganizationMember:
        """Update member's role."""
        member = self.get_member(org_id, user_id)
        if not member:
            raise NotFoundError("Member", str(user_id))
        
        # Check permissions
        self._check_admin_permission(org_id, updated_by)
        
        # Can't demote the owner
        org = self.get_by_id_or_raise(org_id)
        if user_id == org.owner_id and role != "admin":
            raise ValidationError("Cannot change owner's role")
        
        member.role = role
        self.db.commit()
        self.db.refresh(member)
        
        return member
    
    def remove_member(
        self, org_id: UUID, user_id: UUID, removed_by: UUID
    ) -> None:
        """Remove member from organization."""
        member = self.get_member(org_id, user_id)
        if not member:
            raise NotFoundError("Member", str(user_id))
        
        # Check permissions
        self._check_admin_permission(org_id, removed_by)
        
        # Can't remove owner
        org = self.get_by_id_or_raise(org_id)
        if user_id == org.owner_id:
            raise ValidationError("Cannot remove organization owner")
        
        # Revoke team subscription before removing
        self.revoke_team_subscription(org_id, user_id)
        
        self.db.delete(member)
        self.db.commit()
    
    def remove_member_by_user(self, org_id: UUID, user_id: UUID) -> None:
        """
        Remove a member from organization (self-removal, no admin check needed).
        Used when a user leaves an organization on their own.
        """
        member = self.get_member(org_id, user_id)
        if not member:
            raise NotFoundError("Member", str(user_id))
        
        # Can't leave if owner
        org = self.get_by_id_or_raise(org_id)
        if user_id == org.owner_id:
            raise ValidationError("Owner cannot leave organization")
        
        # Revoke team subscription before removing
        self.revoke_team_subscription(org_id, user_id)
        
        self.db.delete(member)
        self.db.commit()
    
    # =========================================================================
    # INVITES
    # =========================================================================
    
    def create_invite(
        self,
        org_id: UUID,
        email: str,
        role: str,
        invited_by: UUID,
    ) -> OrganizationInvitation:
        """Create an invite to join organization."""
        # Check permissions
        self._check_admin_permission(org_id, invited_by)
        
        # Check if user is already a member
        user_result = self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            existing_member = self.get_member(org_id, user.id)
            if existing_member:
                raise ValidationError("User is already a member of this organization")
        
        # Check for existing pending invite
        existing_invite = self.db.execute(
            select(OrganizationInvitation).where(
                and_(
                    OrganizationInvitation.organization_id == org_id,
                    func.lower(OrganizationInvitation.email) == email.lower(),
                    OrganizationInvitation.status == "pending",
                )
            )
        )
        if existing_invite.scalar_one_or_none():
            raise DuplicateError("Invite", "email", email)
        
        # Create invite
        invite = OrganizationInvitation(
            organization_id=org_id,
            email=email.lower(),
            role=role,
            invited_by_id=invited_by,
            token=str(uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=7),
            status="pending",
        )
        
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)
        
        # TODO: Send invite email
        
        return invite
    
    def get_pending_invites(
        self, org_id: UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[OrganizationInvitation], int]:
        """Get pending invites for organization."""
        query = (
            select(OrganizationInvitation)
            .where(
                and_(
                    OrganizationInvitation.organization_id == org_id,
                    OrganizationInvitation.status == "pending",
                    OrganizationInvitation.expires_at > datetime.utcnow(),
                )
            )
            .order_by(OrganizationInvitation.created_at.desc())
        )
        
        count_query = (
            select(func.count(OrganizationInvitation.id))
            .where(
                and_(
                    OrganizationInvitation.organization_id == org_id,
                    OrganizationInvitation.status == "pending",
                    OrganizationInvitation.expires_at > datetime.utcnow(),
                )
            )
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        invites = list(result.scalars().all())
        
        return invites, total
    
    def accept_invite(self, token: str, user_id: UUID) -> OrganizationMember:
        """Accept an organization invite."""
        # Get invite
        result = self.db.execute(
            select(OrganizationInvitation)
            .options(selectinload(OrganizationInvitation.organization))
            .where(OrganizationInvitation.token == token)
        )
        invite = result.scalar_one_or_none()
        
        if not invite:
            raise NotFoundError("Invite", token)
        
        if invite.status != "pending":
            raise ValidationError("Invite has already been used or expired")
        
        if invite.expires_at < datetime.utcnow():
            invite.status = "expired"
            self.db.commit()
            raise ValidationError("Invite has expired")
        
        # Verify email matches
        user_result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user or user.email.lower() != invite.email.lower():
            raise ValidationError("This invite was sent to a different email address")
        
        # Check if already a member
        existing = self.get_member(invite.organization_id, user_id)
        if existing:
            invite.status = "accepted"
            self.db.commit()
            return existing
        
        # Add as member
        member = OrganizationMember(
            organization_id=invite.organization_id,
            user_id=user_id,
            role=invite.role,
            invited_by=invite.invited_by,
        )
        
        invite.status = "accepted"
        invite.accepted_at = datetime.utcnow()
        
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        
        # Grant team subscription if org has Business/Enterprise plan
        self._grant_team_subscription(invite.organization_id, user_id)
        
        return member
    
    def cancel_invite(
        self, org_id: UUID, invite_id: UUID, canceled_by: UUID
    ) -> None:
        """Cancel a pending invite."""
        self._check_admin_permission(org_id, canceled_by)
        
        result = self.db.execute(
            select(OrganizationInvitation).where(
                and_(
                    OrganizationInvitation.id == invite_id,
                    OrganizationInvitation.organization_id == org_id,
                )
            )
        )
        invite = result.scalar_one_or_none()
        
        if not invite:
            raise NotFoundError("Invite", str(invite_id))
        
        invite.status = "canceled"
        self.db.commit()
    
    # =========================================================================
    # USER'S ORGANIZATIONS
    # =========================================================================
    
    def get_user_organizations(
        self, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[Organization], int]:
        """Get organizations a user belongs to."""
        query = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .where(Organization.deleted_at.is_(None))
            .order_by(Organization.name)
        )
        
        count_query = (
            select(func.count(Organization.id))
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .where(Organization.deleted_at.is_(None))
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        orgs = list(result.scalars().all())
        
        return orgs, total
    
    def get_user_pending_invites(
        self, email: str
    ) -> list[OrganizationInvitation]:
        """Get pending invites for a user's email."""
        result = self.db.execute(
            select(OrganizationInvitation)
            .options(selectinload(OrganizationInvitation.organization))
            .where(
                and_(
                    func.lower(OrganizationInvitation.email) == email.lower(),
                    OrganizationInvitation.status == "pending",
                    OrganizationInvitation.expires_at > datetime.utcnow(),
                )
            )
            .order_by(OrganizationInvitation.created_at.desc())
        )
        return list(result.scalars().all())
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = self.db.execute(
            select(Organization).where(Organization.slug == slug.lower())
        )
        return result.scalar_one_or_none()
    
    def _generate_unique_slug(self, name: str) -> str:
        """Generate a unique slug for organization."""
        base_slug = generate_slug(name)
        slug = base_slug
        counter = 1
        
        while self._get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _check_admin_permission(self, org_id: UUID, user_id: UUID) -> None:
        """Check if user is admin of organization."""
        member = self.get_member(org_id, user_id)
        if not member or member.role not in ["admin", "owner"]:
            raise AuthorizationError(
                "You don't have permission to perform this action"
            )
    
    def is_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of organization."""
        member = self.get_member(org_id, user_id)
        return member is not None
    
    def get_member_role(self, org_id: UUID, user_id: UUID) -> Optional[str]:
        """Get user's role in organization."""
        member = self.get_member(org_id, user_id)
        return member.role if member else None
    
    def _grant_team_subscription(self, org_id: UUID, user_id: UUID) -> None:
        """
        Grant a team subscription to a user who joins a Business/Enterprise org.
        
        When a user joins an organization that has a Business or Enterprise plan,
        they automatically inherit that plan's features through an "inherited" 
        subscription linked to the organization.
        """
        from app.models import (
            Organization, Subscription, SubscriptionPlan, SubscriptionStatus,
            BillingCycle, PaymentProvider, SubscriptionTier
        )
        
        # Get the organization
        org = self.get_by_id(org_id)
        if not org:
            return
        
        # Get the organization owner's active subscription
        owner_sub_result = self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == org.owner_id,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
            )
        )
        owner_sub = owner_sub_result.scalar_one_or_none()
        
        if not owner_sub:
            return  # No active subscription on org owner
        
        # Get the plan
        plan_result = self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == owner_sub.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        
        if not plan:
            return
        
        # Only grant if org has Business or Enterprise plan (with team features)
        if plan.tier not in [SubscriptionTier.BUSINESS, SubscriptionTier.ENTERPRISE]:
            return  # Free and Pro don't have team features
        
        # Check if user already has an active subscription
        existing_sub_result = self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
            )
        )
        existing_sub = existing_sub_result.scalar_one_or_none()
        
        if existing_sub:
            # User has their own subscription - mark it's associated with org
            # Don't override if they have a higher plan personally
            existing_plan_result = self.db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.id == existing_sub.plan_id)
            )
            existing_plan = existing_plan_result.scalar_one_or_none()
            
            # Keep their existing subscription but link to org
            if existing_plan and existing_plan.tier in [SubscriptionTier.BEGINNER, SubscriptionTier.PRO]:
                # Upgrade them to the org's plan
                existing_sub.organization_id = org_id
                existing_sub.plan_id = plan.id
                existing_sub.extra_data = existing_sub.extra_data or {}
                existing_sub.extra_data["inherited_from_org"] = str(org_id)
                existing_sub.extra_data["original_plan_id"] = str(existing_plan.id)
                self.db.commit()
            return
        
        # Create new inherited subscription for the user
        from datetime import datetime
        
        new_sub = Subscription(
            id=uuid4(),
            user_id=user_id,
            plan_id=plan.id,
            organization_id=org_id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=owner_sub.billing_cycle,
            current_period_start=owner_sub.current_period_start,
            current_period_end=owner_sub.current_period_end,
            payment_provider=PaymentProvider.MANUAL,  # Inherited, not directly paid
            extra_data={
                "inherited_from_org": str(org_id),
                "inherited_from_owner": str(org.owner_id),
                "type": "team_member_subscription",
            },
        )
        
        self.db.add(new_sub)
        self.db.commit()
    
    def revoke_team_subscription(self, org_id: UUID, user_id: UUID) -> None:
        """
        Revoke team subscription when user leaves organization.
        
        Marks the user's subscription as expired if they don't have 
        their own paid subscription (no free tier available).
        """
        from app.models import Subscription, SubscriptionPlan, SubscriptionStatus, SubscriptionTier
        
        # Find subscription inherited from this org
        sub_result = self.db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.organization_id == org_id,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
            )
        )
        subscription = sub_result.scalar_one_or_none()
        
        if not subscription:
            return
        
        # Check if this was an inherited subscription
        extra_data = subscription.extra_data or {}
        if extra_data.get("inherited_from_org") == str(org_id):
            # Mark subscription as expired (no free tier anymore)
            subscription.status = SubscriptionStatus.EXPIRED
            subscription.organization_id = None
            subscription.extra_data = {
                "downgraded_from_team": str(org_id),
                "downgraded_at": datetime.utcnow().isoformat(),
                "requires_new_subscription": True,
            }
            self.db.commit()


# Dependency injection helper
def get_organization_service(db: AsyncSession) -> OrganizationService:
    """Get organization service instance."""
    return OrganizationService(db)


# =========================================================================
# MODULE-LEVEL HELPER FUNCTIONS (for test compatibility)
# =========================================================================

def check_dataset_access(
    db,
    dataset_id: UUID,
    user_id: UUID,
    required_level: str = "view",
) -> bool:
    """
    Check if user has access to a dataset.
    
    Access can be through:
    1. Direct ownership
    2. Organization membership (shared dataset)
    3. Public dataset
    """
    from app.models import Dataset, OrganizationMember
    
    result = db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        return False
    
    # Owner always has access
    if dataset.user_id == user_id:
        return True
    
    # Public datasets are viewable
    if getattr(dataset, 'is_public', False) and required_level == "view":
        return True
    
    # Check organization access
    if dataset.organization_id:
        member_result = db.execute(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == dataset.organization_id,
                    OrganizationMember.user_id == user_id,
                )
            )
        )
        member = member_result.scalar_one_or_none()
        if member:
            return True
    
    return False


def calculate_team_usage(db, organization_id: UUID) -> dict:
    """
    Calculate usage statistics for an organization.
    """
    from app.models import Dataset, GenerationJob, OrganizationMember
    
    # Get all member IDs
    member_result = db.execute(
        select(OrganizationMember.user_id)
        .where(OrganizationMember.organization_id == organization_id)
    )
    member_ids = [r[0] for r in member_result.all()]
    
    if not member_ids:
        return {
            "rows_generated": 0,
            "storage_used": 0,
            "datasets_count": 0,
        }
    
    # Count datasets
    dataset_count = db.execute(
        select(func.count(Dataset.id))
        .where(Dataset.user_id.in_(member_ids))
        .where(Dataset.deleted_at.is_(None))
    ).scalar() or 0
    
    # Sum rows generated
    rows_generated = db.execute(
        select(func.sum(GenerationJob.row_count))
        .where(GenerationJob.user_id.in_(member_ids))
        .where(GenerationJob.status == "completed")
    ).scalar() or 0
    
    # Sum storage
    storage_bytes = db.execute(
        select(func.sum(GenerationJob.file_size))
        .where(GenerationJob.user_id.in_(member_ids))
        .where(GenerationJob.status == "completed")
    ).scalar() or 0
    
    return {
        "rows_generated": int(rows_generated),
        "storage_used": int(storage_bytes),
        "datasets_count": dataset_count,
    }


def check_team_quota(
    db,
    organization_id: UUID,
    rows_to_generate: int = 1,
) -> bool:
    """
    Check if organization has quota to generate more rows.
    """
    from app.models import Organization
    
    # Get organization and its plan
    result = db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        return False
    
    # Get plan limits
    plan_limits = {
        "free": {"max_rows_per_month": 10000},
        "pro": {"max_rows_per_month": 1000000},
        "business": {"max_rows_per_month": 10000000},
        "enterprise": {"max_rows_per_month": float("inf")},
        "starter": {"max_rows_per_month": 100000},  # Legacy
    }
    
    limits = plan_limits.get(org.plan, plan_limits["free"])
    max_rows = limits.get("max_rows_per_month", 10000)
    
    usage = calculate_team_usage(db, organization_id)
    current_rows = usage.get("rows_generated", 0)
    
    return (current_rows + rows_to_generate) <= max_rows
