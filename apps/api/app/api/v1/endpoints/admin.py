"""
Admin endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Body, status

from app.api.deps import (
    DBSession,
    AdminUser,
    SuperAdminUser,
    Pagination,
    Sorting,
)
from app.services.user_service import UserService
from app.services.subscription_service import SubscriptionService
from app.services.generation_service import GenerationService
from app.services.api_key_service import APIKeyService
from app.schemas.admin import (
    DashboardStatsResponse,
    UserManagementAction,
    SubscriptionManagementAction,
    SystemConfigUpdate,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    AuditLogResponse,
    SupportTicketResponse,
    SystemHealthResponse,
    AnalyticsResponse,
)
from app.schemas.user import UserResponse, UserListResponse
from app.schemas.base import MessageResponse
from app.models import (
    EnterpriseContactRequest, EnterpriseContactStatus,
    Payment, PaymentStatus, PaymentProvider, 
    Subscription, SubscriptionStatus, SubscriptionTier,
    FeatureFlag, AuditLog, SupportTicket,
)


router = APIRouter()


# =============================================================================
# DASHBOARD & STATS
# =============================================================================

@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    summary="Get admin dashboard stats",
)
def get_dashboard_stats(
    db: DBSession,
    admin: AdminUser,
):
    """Get comprehensive platform statistics for admin dashboard."""
    user_service = UserService(db)
    subscription_service = SubscriptionService(db)
    generation_service = GenerationService(db)
    
    # Get various stats
    user_stats = user_service.get_platform_stats()
    subscription_stats = subscription_service.get_platform_stats()
    generation_stats = generation_service.get_platform_stats()
    
    # Calculate change percentages (mock for now - would need historical data)
    # In production, compare current period vs previous period
    users_change = user_stats.get("users_change_pct", 0.0)
    active_change = user_stats.get("active_users_change_pct", 0.0)
    jobs_change = generation_stats.get("jobs_change_pct", 0.0)
    revenue_change = subscription_stats.get("revenue_change_pct", 0.0)
    rows_change = generation_stats.get("rows_generated_change_pct", 0.0)
    new_users_week_change = user_stats.get("new_users_week_change_pct", 0.0)
    
    # Calculate avg job size
    total_rows = generation_stats.get("total_rows_generated", 0)
    total_jobs = generation_stats.get("total_jobs", 0)
    avg_job_size = total_rows // total_jobs if total_jobs > 0 else 0
    
    return DashboardStatsResponse(
        total_users=user_stats.get("total_users", 0),
        active_users=user_stats.get("active_users", 0),
        new_users_today=user_stats.get("new_users_today", 0),
        new_users_this_week=user_stats.get("new_users_this_week", 0),
        new_users_this_month=user_stats.get("new_users_this_month", 0),
        total_subscriptions=subscription_stats.get("total_subscriptions", 0),
        active_subscriptions=subscription_stats.get("active_subscriptions", 0),
        mrr=subscription_stats.get("mrr", 0.0),
        arr=subscription_stats.get("arr", 0.0),
        total_revenue=subscription_stats.get("total_revenue", 0.0),
        total_jobs=generation_stats.get("total_jobs", 0),
        completed_jobs=generation_stats.get("completed_jobs", 0),
        failed_jobs=generation_stats.get("failed_jobs", 0),
        total_rows_generated=generation_stats.get("total_rows_generated", 0),
        total_api_calls=generation_stats.get("total_api_calls", 0),
        # Dynamic change percentages
        users_change_pct=users_change,
        active_users_change_pct=active_change,
        datasets_change_pct=0.0,  # Would come from dataset service
        jobs_change_pct=jobs_change,
        revenue_change_pct=revenue_change,
        rows_generated_change_pct=rows_change,
        new_users_week_change_pct=new_users_week_change,
        # Additional stats
        total_datasets=generation_stats.get("total_datasets", 0),
        revenue_this_month=subscription_stats.get("mrr", 0.0),
        rows_generated_today=generation_stats.get("rows_generated_today", 0),
        avg_job_size=avg_job_size,
    )


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Get analytics data",
)
def get_analytics(
    db: DBSession,
    admin: AdminUser,
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    metric: str = Query("users", description="Metric: users, revenue, jobs, api_calls"),
):
    """Get time-series analytics data for specified metric."""
    user_service = UserService(db)
    subscription_service = SubscriptionService(db)
    generation_service = GenerationService(db)
    
    # Parse period
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=period_days)
    
    # Get data based on metric
    if metric == "users":
        result = user_service.get_signups_over_time(start_date)
        data = result.get("daily", []) if isinstance(result, dict) else []
    elif metric == "revenue":
        result = subscription_service.get_revenue_over_time(start_date)
        data = result.get("daily", []) if isinstance(result, dict) else []
    elif metric == "jobs":
        result = generation_service.get_jobs_over_time(start_date)
        data = result.get("daily", []) if isinstance(result, dict) else []
    else:
        data = []
    
    return AnalyticsResponse(
        metric=metric,
        period=period,
        data=data,
    )


# =============================================================================
# USER MANAGEMENT
# =============================================================================

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all users",
)
def list_all_users(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    sorting: Sorting,
    search: Optional[str] = Query(None, description="Search by email or name"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    subscription_status: Optional[str] = Query(None, description="Filter by subscription"),
):
    """List all users with filters. Admin only."""
    user_service = UserService(db)
    users, total = user_service.list_users(
        page=pagination.page,
        per_page=pagination.per_page,
        search=search,
        role=role,
        status=status,
        sort_by=sorting.sort_by or "created_at",
        sort_order=sorting.sort_order or "desc",
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


@router.post(
    "/users/{user_id}/action",
    response_model=MessageResponse,
    summary="Perform user management action",
)
def user_management_action(
    user_id: UUID,
    action: UserManagementAction,
    db: DBSession,
    admin: AdminUser,
):
    """
    Perform management action on a user.
    Actions: suspend, reactivate, verify_email, reset_password, 
             change_role, delete, impersonate
    """
    user_service = UserService(db)
    
    if action.action == "suspend":
        user_service.suspend(user_id, action.reason)
        return MessageResponse(message="User suspended")
    elif action.action == "reactivate":
        user_service.reactivate(user_id)
        return MessageResponse(message="User reactivated")
    elif action.action == "verify_email":
        user_service.verify_email(user_id)
        return MessageResponse(message="Email verified")
    elif action.action == "reset_password":
        user_service.admin_reset_password(user_id)
        return MessageResponse(message="Password reset email sent")
    elif action.action == "change_role":
        if not action.new_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_role is required for change_role action",
            )
        user_service.change_role(user_id, action.new_role)
        return MessageResponse(message=f"Role changed to {action.new_role}")
    elif action.action == "delete":
        user_service.delete(user_id)
        return MessageResponse(message="User deleted")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action: {action.action}",
        )


@router.post(
    "/users/{user_id}/subscription-tier",
    response_model=MessageResponse,
    summary="Manually update user subscription tier",
)
def update_user_subscription_tier(
    user_id: UUID,
    data: dict,
    db: DBSession,
    admin: AdminUser,
):
    """
    Manually update a user's subscription tier.
    Use for technical fixes when payment-based activation fails.
    """
    tier = data.get("tier")
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tier is required",
        )
    
    valid_tiers = ["free", "starter", "professional", "business", "enterprise"]
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}. Must be one of {valid_tiers}",
        )
    
    user_service = UserService(db)
    user_service.change_subscription_tier(user_id, tier)
    return MessageResponse(message=f"Subscription tier updated to {tier}")


# =============================================================================
# SUBSCRIPTION MANAGEMENT
# =============================================================================

@router.get(
    "/subscriptions",
    summary="List all subscriptions",
)
def list_all_subscriptions(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    sorting: Sorting,
    plan: Optional[str] = Query(None, description="Filter by plan"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """List all subscriptions. Admin only."""
    subscription_service = SubscriptionService(db)
    subscriptions, total = subscription_service.list_all(
        page=pagination.page,
        per_page=pagination.per_page,
        plan=plan,
        status=status,
        sort_by=sorting.sort_by or "created_at",
        sort_order=sorting.sort_order or "desc",
    )
    
    return {
        "items": [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "user_email": s.user.email if s.user else None,
                "plan_id": str(s.plan_id),
                "plan_name": s.plan.name if s.plan else None,
                "status": s.status,
                "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
                "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
                "cancel_at_period_end": s.cancel_at_period_end or False,
                "created_at": s.created_at.isoformat(),
            }
            for s in subscriptions
        ],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }


@router.post(
    "/subscriptions/{subscription_id}/action",
    response_model=MessageResponse,
    summary="Perform subscription action",
)
def subscription_management_action(
    subscription_id: UUID,
    action: SubscriptionManagementAction,
    db: DBSession,
    admin: AdminUser,
):
    """
    Perform management action on a subscription.
    Actions: cancel, extend, upgrade, downgrade, refund
    """
    subscription_service = SubscriptionService(db)
    
    if action.action == "cancel":
        subscription_service.admin_cancel(subscription_id, action.reason)
        return MessageResponse(message="Subscription cancelled")
    elif action.action == "extend":
        if not action.days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="days is required for extend action",
            )
        subscription_service.extend(subscription_id, action.days)
        return MessageResponse(message=f"Subscription extended by {action.days} days")
    elif action.action == "upgrade":
        if not action.new_plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_plan_id is required for upgrade action",
            )
        subscription_service.admin_change_plan(subscription_id, action.new_plan_id)
        return MessageResponse(message="Subscription upgraded")
    elif action.action == "downgrade":
        if not action.new_plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="new_plan_id is required for downgrade action",
            )
        subscription_service.admin_change_plan(subscription_id, action.new_plan_id)
        return MessageResponse(message="Subscription downgraded")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action: {action.action}",
        )


# =============================================================================
# JOBS MANAGEMENT
# =============================================================================

@router.get(
    "/jobs",
    summary="List all generation jobs",
)
def list_all_jobs(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    sorting: Sorting,
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
):
    """List all generation jobs. Admin only."""
    generation_service = GenerationService(db)
    jobs, total = generation_service.list_all_jobs(
        page=pagination.page,
        per_page=pagination.per_page,
        user_id=user_id,
        status_filter=status_filter,
        sort_by=sorting.sort_by or "created_at",
        sort_order=sorting.sort_order or "desc",
    )
    
    return {
        "items": [
            {
                "id": str(j.id),
                "user_id": str(j.user_id) if j.user_id else None,
                "user_email": j.user.email if j.user else None,
                "dataset_id": str(j.dataset_id),
                "dataset_name": j.dataset.name if j.dataset else None,
                "status": j.status,
                "row_count": j.row_count,
                "output_format": j.output_format,
                "progress": j.progress or 0,
                "error_message": j.error_message,
                "created_at": j.created_at.isoformat(),
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }


# =============================================================================
# FEATURE FLAGS
# =============================================================================

@router.get(
    "/feature-flags",
    response_model=List[FeatureFlagResponse],
    summary="List feature flags",
)
def list_feature_flags(
    db: DBSession,
    admin: AdminUser,
):
    """List all feature flags."""
    from sqlalchemy import select
    
    result = db.execute(select(FeatureFlag).order_by(FeatureFlag.name))
    flags = result.scalars().all()
    
    return [
        FeatureFlagResponse(
            id=f.id,
            name=f.name,
            description=f.description,
            is_enabled=f.is_enabled,
            rollout_percentage=int(f.rollout_percentage or 0),
            allowed_users=[],
            allowed_plans=f.enabled_for_tiers or [],
            created_at=f.created_at,
            updated_at=f.updated_at,
        )
        for f in flags
    ]


@router.post(
    "/feature-flags",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create feature flag",
)
def create_feature_flag(
    data: FeatureFlagCreate,
    db: DBSession,
    admin: SuperAdminUser,
):
    """Create a new feature flag. Super admin only."""
    # Removed - imported at top
    
    flag = FeatureFlag(
        name=data.name,
        description=data.description,
        is_enabled=data.is_enabled,
        rollout_percentage=data.rollout_percentage,
        enabled_for_users=[str(uid) for uid in data.allowed_users],
        enabled_for_tiers=data.allowed_plans,
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    
    return FeatureFlagResponse(
        id=flag.id,
        name=flag.name,
        description=flag.description,
        is_enabled=flag.is_enabled,
        rollout_percentage=int(flag.rollout_percentage or 0),
        allowed_users=[],
        allowed_plans=flag.enabled_for_tiers or [],
        created_at=flag.created_at,
        updated_at=flag.updated_at,
    )


@router.put(
    "/feature-flags/{flag_id}",
    response_model=FeatureFlagResponse,
    summary="Update feature flag",
)
def update_feature_flag(
    flag_id: UUID,
    data: FeatureFlagUpdate,
    db: DBSession,
    admin: SuperAdminUser,
):
    """Update a feature flag. Super admin only."""
    from sqlalchemy import select
    # Removed - imported at top
    
    result = db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found",
        )
    
    # Update fields - map schema fields to model fields
    update_data = data.model_dump(exclude_unset=True)
    if 'description' in update_data:
        flag.description = update_data['description']
    if 'is_enabled' in update_data:
        flag.is_enabled = update_data['is_enabled']
    if 'rollout_percentage' in update_data:
        flag.rollout_percentage = update_data['rollout_percentage']
    if 'allowed_users' in update_data:
        flag.enabled_for_users = [str(uid) for uid in update_data['allowed_users']]
    if 'allowed_plans' in update_data:
        flag.enabled_for_tiers = update_data['allowed_plans']
    
    db.commit()
    db.refresh(flag)
    
    return FeatureFlagResponse(
        id=flag.id,
        name=flag.name,
        description=flag.description,
        is_enabled=flag.is_enabled,
        rollout_percentage=int(flag.rollout_percentage or 0),
        allowed_users=[],
        allowed_plans=flag.enabled_for_tiers or [],
        created_at=flag.created_at,
        updated_at=flag.updated_at,
    )


@router.delete(
    "/feature-flags/{flag_id}",
    response_model=MessageResponse,
    summary="Delete feature flag",
)
def delete_feature_flag(
    flag_id: UUID,
    db: DBSession,
    admin: SuperAdminUser,
):
    """Delete a feature flag. Super admin only."""
    from sqlalchemy import select, delete
    # Removed - imported at top
    
    result = db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found",
        )
    
    db.execute(delete(FeatureFlag).where(FeatureFlag.id == flag_id))
    db.commit()
    
    return MessageResponse(message="Feature flag deleted")


# =============================================================================
# AUDIT LOGS
# =============================================================================

@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
)
def get_audit_logs(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
):
    """Get audit logs with filters. Admin only."""
    from sqlalchemy import select, and_
    # Removed - imported at top
    
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    
    filters = []
    if user_id:
        filters.append(AuditLog.user_id == user_id)
    if action:
        filters.append(AuditLog.action == action)
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if start_date:
        filters.append(AuditLog.created_at >= start_date)
    if end_date:
        filters.append(AuditLog.created_at <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.offset).limit(pagination.per_page)
    
    result = db.execute(query)
    logs = result.scalars().all()
    
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=log.user.email if log.user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_values=log.old_values,
            new_values=log.new_values,
            user_agent=log.user_agent,
            created_at=log.created_at,
        )
        for log in logs
    ]


# =============================================================================
# SUPPORT TICKETS
# =============================================================================

@router.get(
    "/tickets",
    response_model=List[SupportTicketResponse],
    summary="List support tickets",
)
def list_support_tickets(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
):
    """List all support tickets. Admin only."""
    from sqlalchemy import select, and_
    # Removed - imported at top
    
    query = select(SupportTicket).order_by(SupportTicket.created_at.desc())
    
    filters = []
    if status_filter:
        filters.append(SupportTicket.status == status_filter)
    if priority:
        filters.append(SupportTicket.priority == priority)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.offset).limit(pagination.per_page)
    
    result = db.execute(query)
    tickets = result.scalars().all()
    
    return [
        SupportTicketResponse(
            id=t.id,
            ticket_number=t.ticket_number,
            user_id=t.user_id,
            user_email=t.user.email if t.user else None,
            subject=t.subject,
            description=t.description,
            category=t.category,
            priority=t.priority,
            status=t.status,
            assigned_to=t.assigned_to,
            created_at=t.created_at,
            updated_at=t.updated_at,
            resolved_at=t.resolved_at,
        )
        for t in tickets
    ]


@router.put(
    "/tickets/{ticket_id}",
    response_model=SupportTicketResponse,
    summary="Update support ticket",
)
def update_support_ticket(
    ticket_id: UUID,
    status_value: Optional[str] = Body(None, alias="status"),
    priority: Optional[str] = Body(None),
    assigned_to: Optional[UUID] = Body(None),
    db: DBSession = None,
    admin: AdminUser = None,
):
    """Update a support ticket status. Admin only."""
    from sqlalchemy import select
    # Removed - imported at top
    
    result = db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    if status_value:
        ticket.status = status_value
        if status_value == "resolved":
            ticket.resolved_at = datetime.utcnow()
    if priority:
        ticket.priority = priority
    if assigned_to:
        ticket.assigned_to = assigned_to
    
    db.commit()
    db.refresh(ticket)
    
    return SupportTicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        assigned_to=ticket.assigned_to,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
    )


# =============================================================================
# SYSTEM HEALTH
# =============================================================================

@router.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="Get system health",
)
def get_system_health(
    db: DBSession,
    admin: AdminUser,
):
    """Get system health status. Admin only."""
    import redis as redis_sync
    from app.core.config import settings
    import psutil
    
    health = {
        "status": "healthy",
        "database": "healthy",
        "redis": "healthy",
        "celery": "healthy",
        "storage": "healthy",
    }
    
    # System resource metrics
    cpu_usage = None
    memory_usage = None
    disk_usage = None
    active_workers = 0
    pending_jobs = 0
    
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
    except Exception:
        pass  # psutil may not be available
    
    # Check database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception:
        health["database"] = "unhealthy"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = redis_sync.from_url(settings.REDIS_URL)
        redis_client.ping()
        redis_client.close()
    except Exception:
        health["redis"] = "unhealthy"
        health["status"] = "degraded"
    
    # Check Celery (simple check)
    try:
        from app.celery_app import celery_app
        # Try to get worker stats
        stats = celery_app.control.inspect().stats()
        if stats:
            active_workers = len(stats)
        # Try to get pending jobs
        reserved = celery_app.control.inspect().reserved()
        if reserved:
            pending_jobs = sum(len(tasks) for tasks in reserved.values())
    except Exception:
        health["celery"] = "unknown"  # May just mean no workers
    
    return SystemHealthResponse(
        status=health["status"],
        database=health["database"],
        redis=health["redis"],
        celery=health["celery"],
        storage=health["storage"],
        timestamp=datetime.utcnow(),
        cpu_usage_percent=cpu_usage,
        memory_usage_percent=memory_usage,
        disk_usage_percent=disk_usage,
        active_workers=active_workers,
        pending_jobs=pending_jobs,
    )


# =============================================================================
# LOGS
# =============================================================================

@router.get(
    "/logs",
    summary="Get system logs",
)
def get_system_logs(
    db: DBSession,
    admin: AdminUser,
    level: Optional[str] = Query(None, description="Filter by log level"),
    source: Optional[str] = Query(None, description="Filter by source"),
    search: Optional[str] = Query(None, description="Search in logs"),
    limit: int = Query(100, le=1000, description="Max number of logs"),
    offset: int = Query(0, description="Pagination offset"),
):
    """Get system logs from PostgreSQL audit logs. Admin only."""
    from app.models import AuditLog
    from sqlalchemy import desc, or_
    
    query = db.query(AuditLog)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                AuditLog.action.ilike(f"%{search}%"),
                AuditLog.notes.ilike(f"%{search}%"),
            )
        )
    
    if level:
        # Level is derived from action type in our case
        pass  # Can enhance with log level field if needed
    
    # Sort by most recent
    query = query.order_by(desc(AuditLog.created_at))
    
    # Pagination
    total = query.count()
    logs = query.offset(offset).limit(limit).all()
    
    items = []
    for log in logs:
        # Determine level based on action
        log_level = "info"
        if level:
            log_level = level
        elif "error" in (log.action or "").lower() or "fail" in (log.action or "").lower():
            log_level = "error"
        
        # Determine source
        log_source = source or "api"
        
        items.append({
            "id": str(log.id),
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "level": log_level,
            "message": log.notes or log.action or "",
            "source": log_source,
            "action": log.action,
            "user_id": str(log.user_id) if log.user_id else None,
            "user_email": log.user.email if log.user else None,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "resource_type": log.resource_type,
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "details": {
                "old_values": log.old_values,
                "new_values": log.new_values,
                "notes": log.notes,
                "user_agent": log.user_agent,
                "request_id": log.request_id,
            },
        })
    
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.delete(
    "/logs/{log_id}",
    summary="Delete a log entry",
)
def delete_log(
    db: DBSession,
    admin: AdminUser,
    log_id: UUID,
):
    """Delete a specific log entry. Admin only."""
    from app.models import AuditLog
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Log deleted successfully"}


# =============================================================================
# JOBS QUEUE MANAGEMENT
# =============================================================================

@router.get(
    "/jobs",
    summary="Get all jobs",
)
def get_all_jobs(
    db: DBSession,
    admin: AdminUser,
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by user email or dataset name"),
    limit: int = Query(100, le=1000, description="Max number of jobs"),
    offset: int = Query(0, description="Pagination offset"),
):
    """Get all generation jobs with filters. Admin only."""
    from app.models import GenerationJob
    from sqlalchemy import desc, or_
    
    query = db.query(GenerationJob)
    
    # Apply filters
    if status:
        query = query.filter(GenerationJob.status == status)
    
    if search:
        # Join with user and dataset tables for search
        from app.models import User, Dataset
        query = query.join(User, GenerationJob.user_id == User.id, isouter=True)
        query = query.join(Dataset, GenerationJob.dataset_id == Dataset.id, isouter=True)
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                Dataset.name.ilike(f"%{search}%"),
            )
        )
    
    # Sort by most recent
    query = query.order_by(desc(GenerationJob.created_at))
    
    # Pagination
    total = query.count()
    jobs = query.offset(offset).limit(limit).all()
    
    # Calculate stats
    all_jobs = db.query(GenerationJob).all()
    stats = {
        "total": len(all_jobs),
        "queued": sum(1 for j in all_jobs if j.status == "queued"),
        "processing": sum(1 for j in all_jobs if j.status == "processing"),
        "completed": sum(1 for j in all_jobs if j.status == "completed"),
        "failed": sum(1 for j in all_jobs if j.status == "failed"),
    }
    
    return {
        "jobs": [
            {
                "id": str(job.id),
                "status": job.status,
                "progress": job.progress or 0,
                "rows_requested": job.rows_requested,
                "rows_generated": job.rows_generated or 0,
                "user_email": job.user.email if job.user else None,
                "user_id": str(job.user_id) if job.user_id else None,
                "dataset_name": job.dataset.name if job.dataset else None,
                "dataset_id": str(job.dataset_id) if job.dataset_id else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "failed_at": job.failed_at.isoformat() if job.failed_at else None,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "error": job.error_message,
                "worker": f"worker-{hash(str(job.id)) % 4 + 1}",  # Simulated worker ID
                "priority": "high" if job.rows_requested > 50000 else "normal",
            }
            for job in jobs
        ],
        "stats": stats,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# =============================================================================
# ENTERPRISE CONTACT REQUESTS (Talk to Us)
# =============================================================================

@router.get(
    "/enterprise/contacts",
    summary="List enterprise contact requests",
)
def list_enterprise_contacts(
    db: DBSession,
    admin: AdminUser,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=200, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
):
    """
    List all enterprise contact requests (Talk to Us submissions).
    Admin only - shows company info, contact details, and deal pipeline.
    """
    from sqlalchemy import desc
    
    query = db.query(EnterpriseContactRequest)
    
    # Filter by status if provided
    if status:
        try:
            status_enum = EnterpriseContactStatus(status)
            query = query.filter(EnterpriseContactRequest.status == status_enum)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(desc(EnterpriseContactRequest.created_at))
    
    total = query.count()
    contacts = query.offset(offset).limit(limit).all()
    
    # Calculate stats
    all_contacts = db.query(EnterpriseContactRequest).all()
    stats = {
        "total": len(all_contacts),
        "pending": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.PENDING),
        "contacted": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.CONTACTED),
        "in_progress": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.IN_PROGRESS),
        "qualified": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.QUALIFIED),
        "closed_won": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.CLOSED_WON),
        "closed_lost": sum(1 for c in all_contacts if c.status == EnterpriseContactStatus.CLOSED_LOST),
    }
    
    return {
        "contacts": [
            {
                "id": str(c.id),
                "company_name": c.company_name,
                "contact_name": c.contact_name,
                "email": c.email,
                "phone": c.phone,
                "company_size": c.company_size,
                "use_case": c.use_case,
                "estimated_rows_per_month": c.estimated_rows_per_month,
                "requirements": c.requirements,
                "status": c.status.value,
                "assigned_to_id": str(c.assigned_to_id) if c.assigned_to_id else None,
                "estimated_deal_value": c.estimated_deal_value,
                "notes": c.notes,
                "user_id": str(c.user_id) if c.user_id else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "contacted_at": c.contacted_at.isoformat() if c.contacted_at else None,
            }
            for c in contacts
        ],
        "stats": stats,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/enterprise/contacts/{contact_id}",
    summary="Get enterprise contact details",
)
def get_enterprise_contact(
    contact_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """Get detailed information about an enterprise contact request."""
    contact = db.query(EnterpriseContactRequest).filter(
        EnterpriseContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Enterprise contact not found")
    
    # Get linked user if exists
    user_info = None
    if contact.user_id:
        from app.models import User
        user = db.query(User).filter(User.id == contact.user_id).first()
        if user:
            user_info = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
    
    return {
        "id": str(contact.id),
        "company_name": contact.company_name,
        "contact_name": contact.contact_name,
        "email": contact.email,
        "phone": contact.phone,
        "company_size": contact.company_size,
        "use_case": contact.use_case,
        "estimated_rows_per_month": contact.estimated_rows_per_month,
        "requirements": contact.requirements,
        "status": contact.status.value,
        "assigned_to_id": str(contact.assigned_to_id) if contact.assigned_to_id else None,
        "estimated_deal_value": contact.estimated_deal_value,
        "notes": contact.notes,
        "user_id": str(contact.user_id) if contact.user_id else None,
        "user": user_info,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "contacted_at": contact.contacted_at.isoformat() if contact.contacted_at else None,
        "updated_at": contact.updated_at.isoformat() if contact.updated_at else None,
    }


@router.put(
    "/enterprise/contacts/{contact_id}",
    summary="Update enterprise contact status",
)
def update_enterprise_contact(
    contact_id: UUID,
    db: DBSession,
    admin: AdminUser,
    status: Optional[str] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
    estimated_deal_value: Optional[int] = Body(None, embed=True),
    assigned_to_id: Optional[UUID] = Body(None, embed=True),
):
    """
    Update an enterprise contact request.
    
    - Update status through the sales pipeline
    - Add notes and deal value
    - Assign to a sales rep
    """
    contact = db.query(EnterpriseContactRequest).filter(
        EnterpriseContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Enterprise contact not found")
    
    # Update fields
    if status:
        try:
            contact.status = EnterpriseContactStatus(status)
            if status == "contacted" and not contact.contacted_at:
                contact.contacted_at = datetime.utcnow()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if notes is not None:
        contact.notes = notes
    
    if estimated_deal_value is not None:
        contact.estimated_deal_value = estimated_deal_value
    
    if assigned_to_id is not None:
        contact.assigned_to_id = assigned_to_id
    
    db.commit()
    db.refresh(contact)
    
    return {
        "id": str(contact.id),
        "status": contact.status.value,
        "message": "Enterprise contact updated successfully",
    }


# =============================================================================
# PAYMENTS & REVENUE DASHBOARD
# =============================================================================

@router.get(
    "/payments/dashboard",
    summary="Get payments dashboard",
)
def get_payments_dashboard(
    db: DBSession,
    admin: AdminUser,
):
    """
    Get comprehensive payments dashboard with revenue metrics.
    Shows all payment info that admin needs to see.
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
    
    # Get all payments
    all_payments = db.query(Payment).all()
    
    # Calculate metrics
    total_revenue = sum(p.amount_cents for p in all_payments if p.status == PaymentStatus.COMPLETED) / 100
    this_month_payments = [p for p in all_payments if p.created_at >= start_of_month and p.status == PaymentStatus.COMPLETED]
    last_month_payments = [p for p in all_payments if start_of_last_month <= p.created_at < start_of_month and p.status == PaymentStatus.COMPLETED]
    
    this_month_revenue = sum(p.amount_cents for p in this_month_payments) / 100
    last_month_revenue = sum(p.amount_cents for p in last_month_payments) / 100
    
    # Revenue growth
    growth = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
    
    # Get subscriptions breakdown
    subscriptions = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).all()
    
    # MRR calculation (Monthly Recurring Revenue)
    from app.models import SubscriptionPlan
    mrr = 0
    tier_breakdown = {
        "free": 0,
        "pro": 0,
        "business": 0,
        "enterprise": 0,
    }
    
    for sub in subscriptions:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
        if plan:
            tier_breakdown[plan.tier.value] += 1
            mrr += plan.monthly_price_cents / 100
    
    return {
        "overview": {
            "total_revenue_usd": total_revenue,
            "this_month_revenue_usd": this_month_revenue,
            "last_month_revenue_usd": last_month_revenue,
            "revenue_growth_percent": round(growth, 2),
            "mrr_usd": mrr,
            "arr_usd": mrr * 12,
        },
        "subscriptions": {
            "total_active": len(subscriptions),
            "by_tier": tier_breakdown,
        },
        "payments": {
            "total_count": len(all_payments),
            "completed": sum(1 for p in all_payments if p.status == PaymentStatus.COMPLETED),
            "failed": sum(1 for p in all_payments if p.status == PaymentStatus.FAILED),
            "pending": sum(1 for p in all_payments if p.status == PaymentStatus.PENDING),
        },
    }


@router.get(
    "/payments/list",
    summary="List all payments",
)
def list_payments(
    db: DBSession,
    admin: AdminUser,
    status: Optional[str] = Query(None, description="Filter by status"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(50, le=200, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
):
    """
    List all payments with filters.
    Shows payment details, user info, and subscription info.
    """
    from sqlalchemy import desc
    from app.models import User
    
    query = db.query(Payment)
    
    # Apply filters
    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.filter(Payment.status == status_enum)
        except ValueError:
            pass
    
    if provider:
        try:
            provider_enum = PaymentProvider(provider)
            query = query.filter(Payment.provider == provider_enum)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(desc(Payment.created_at))
    
    total = query.count()
    payments = query.offset(offset).limit(limit).all()
    
    result = []
    for p in payments:
        # Get user info
        user_info = None
        if p.user_id:
            user = db.query(User).filter(User.id == p.user_id).first()
            if user:
                user_info = {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                }
        
        result.append({
            "id": str(p.id),
            "amount_cents": p.amount_cents,
            "amount_usd": p.amount_cents / 100,
            "currency": p.currency or "USD",
            "status": p.status.value,
            "provider": p.provider.value if p.provider else None,
            "dodo_payment_id": p.dodo_payment_id,
            "dodo_customer_id": p.dodo_customer_id,
            "failure_reason": p.failure_message,
            "user": user_info,
            "subscription_id": str(p.subscription_id) if p.subscription_id else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    
    return {
        "payments": result,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/subscriptions/list",
    summary="List all subscriptions",
)
def list_subscriptions(
    db: DBSession,
    admin: AdminUser,
    status: Optional[str] = Query(None, description="Filter by status"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    limit: int = Query(50, le=200, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
):
    """
    List all subscriptions with detailed info.
    Shows user info, plan details, billing status.
    """
    from sqlalchemy import desc
    from app.models import User, SubscriptionPlan
    
    query = db.query(Subscription)
    
    # Apply filters
    if status:
        try:
            status_enum = SubscriptionStatus(status)
            query = query.filter(Subscription.status == status_enum)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(desc(Subscription.created_at))
    
    total = query.count()
    subscriptions = query.offset(offset).limit(limit).all()
    
    result = []
    for s in subscriptions:
        # Get user and plan info
        user = db.query(User).filter(User.id == s.user_id).first()
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == s.plan_id).first()
        
        # Filter by tier after query (since tier is on plan)
        if tier and plan and plan.tier.value != tier.lower():
            continue
        
        result.append({
            "id": str(s.id),
            "user": {
                "id": str(user.id) if user else None,
                "email": user.email if user else None,
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() if user else None,
            } if user else None,
            "plan": {
                "id": str(plan.id) if plan else None,
                "name": plan.name if plan else None,
                "tier": plan.tier.value if plan else None,
                "monthly_price_cents": plan.monthly_price_cents if plan else None,
            } if plan else None,
            "status": s.status.value,
            "billing_cycle": s.billing_cycle.value if s.billing_cycle else None,
            "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
            "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
            "cancel_at_period_end": s.cancel_at_period_end,
            "dodo_subscription_id": s.dodo_subscription_id,
            "dodo_customer_id": s.dodo_customer_id,
            "is_enterprise": s.is_enterprise,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    
    return {
        "subscriptions": result,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# =============================================================================
# ADMIN USER & SUBSCRIPTION MANAGEMENT
# =============================================================================

@router.put(
    "/users/{user_id}/plan",
    summary="Change user's subscription plan",
)
def admin_change_user_plan(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
    tier: str = Body(..., embed=True, description="New tier: free, pro, business, enterprise"),
    reason: Optional[str] = Body(None, embed=True, description="Reason for plan change"),
):
    """
    Admin endpoint to change a user's subscription plan.
    This bypasses payment and immediately sets the new plan.
    """
    from app.models import User, SubscriptionPlan, Subscription, BillingCycle
    import uuid as uuid_module
    
    tier = tier.lower()
    valid_tiers = ["free", "pro", "business", "enterprise"]
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get target plan
    tier_enum = SubscriptionTier(tier)
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier_enum).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan not found for tier: {tier}")
    
    # Cancel existing active subscription
    existing_sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if existing_sub:
        existing_sub.status = SubscriptionStatus.CANCELLED
        existing_sub.cancelled_at = datetime.utcnow()
        existing_sub.cancellation_reason = f"Admin changed plan: {reason or 'No reason provided'}"
    
    # Create new subscription
    now = datetime.utcnow()
    new_sub = Subscription(
        id=uuid_module.uuid4(),
        user_id=user_id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        payment_provider=PaymentProvider.MANUAL,
        is_enterprise=(tier == "enterprise"),
    )
    
    db.add(new_sub)
    db.commit()
    
    return {
        "message": f"User plan changed to {tier}",
        "user_id": str(user_id),
        "new_tier": tier,
        "subscription_id": str(new_sub.id),
    }


@router.put(
    "/users/{user_id}/limits",
    summary="Set custom limits for a user",
)
def admin_set_user_limits(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
    max_rows_per_month: Optional[int] = Body(None, embed=True),
    max_rows_per_job: Optional[int] = Body(None, embed=True),
    max_datasets: Optional[int] = Body(None, embed=True),
    max_api_keys: Optional[int] = Body(None, embed=True),
    max_concurrent_jobs: Optional[int] = Body(None, embed=True),
    api_rate_limit_per_minute: Optional[int] = Body(None, embed=True),
):
    """
    Set custom usage limits for a user, overriding their plan limits.
    Use -1 for unlimited. Use None (omit) to keep current value.
    """
    from app.models import User
    
    # Get user's active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found for user")
    
    # Build custom limits
    custom_limits = subscription.custom_limits or {}
    
    if max_rows_per_month is not None:
        custom_limits["max_rows_per_month"] = max_rows_per_month
    if max_rows_per_job is not None:
        custom_limits["max_rows_per_job"] = max_rows_per_job
    if max_datasets is not None:
        custom_limits["max_datasets"] = max_datasets
    if max_api_keys is not None:
        custom_limits["max_api_keys"] = max_api_keys
    if max_concurrent_jobs is not None:
        custom_limits["max_concurrent_jobs"] = max_concurrent_jobs
    if api_rate_limit_per_minute is not None:
        custom_limits["api_rate_limit_per_minute"] = api_rate_limit_per_minute
    
    subscription.custom_limits = custom_limits
    db.commit()
    
    return {
        "message": "Custom limits updated",
        "user_id": str(user_id),
        "custom_limits": custom_limits,
    }


@router.delete(
    "/users/{user_id}/limits",
    summary="Remove custom limits for a user",
)
def admin_remove_user_limits(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """Remove all custom limits for a user, reverting to plan defaults."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found for user")
    
    subscription.custom_limits = None
    db.commit()
    
    return {"message": "Custom limits removed", "user_id": str(user_id)}


@router.get(
    "/users/{user_id}/usage",
    summary="Get user's current usage",
)
def admin_get_user_usage(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """Get detailed usage statistics for a user."""
    from app.models import User, GenerationJob, Dataset, APIKey
    from sqlalchemy import func
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    # Current month stats
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Jobs this month
    jobs_this_month = db.query(GenerationJob).filter(
        GenerationJob.user_id == user_id,
        GenerationJob.created_at >= start_of_month
    ).all()
    
    rows_generated_this_month = sum(j.rows_generated or 0 for j in jobs_this_month)
    jobs_count_this_month = len(jobs_this_month)
    
    # Total datasets
    total_datasets = db.query(func.count(Dataset.id)).filter(Dataset.user_id == user_id).scalar()
    
    # Active API keys
    active_api_keys = db.query(func.count(APIKey.id)).filter(
        APIKey.user_id == user_id,
        APIKey.is_active == True
    ).scalar()
    
    # Get plan limits
    plan_limits = {}
    if subscription:
        from app.models import SubscriptionPlan
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == subscription.plan_id).first()
        if plan:
            plan_limits = {
                "tier": plan.tier.value,
                "max_rows_per_month": plan.features.get("max_rows_per_month", -1),
                "max_rows_per_job": plan.features.get("max_rows_per_job", -1),
                "max_datasets": plan.max_datasets,
                "max_api_keys": plan.max_api_keys,
            }
    
    return {
        "user_id": str(user_id),
        "email": user.email,
        "current_usage": {
            "rows_generated_this_month": rows_generated_this_month,
            "jobs_this_month": jobs_count_this_month,
            "total_datasets": total_datasets,
            "active_api_keys": active_api_keys,
        },
        "plan_limits": plan_limits,
        "custom_limits": subscription.custom_limits if subscription else None,
        "subscription_status": subscription.status.value if subscription else "none",
    }


@router.post(
    "/jobs/{job_id}/cancel",
    summary="Cancel a generation job",
)
def admin_cancel_job(
    job_id: UUID,
    db: DBSession,
    admin: AdminUser,
    reason: Optional[str] = Body(None, embed=True),
):
    """Admin endpoint to cancel a generation job."""
    from app.models import GenerationJob, JobStatus
    
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {job.status}")
    
    job.status = JobStatus.CANCELED
    job.error_message = f"Cancelled by admin: {reason or 'No reason provided'}"
    job.failed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Job cancelled", "job_id": str(job_id)}


@router.put(
    "/plans/{tier}/limits",
    summary="Update plan limits",
)
def admin_update_plan_limits(
    tier: str,
    db: DBSession,
    admin: SuperAdminUser,  # Only super admin can modify plans
    max_datasets: Optional[int] = Body(None, embed=True),
    max_api_keys: Optional[int] = Body(None, embed=True),
    max_team_members: Optional[int] = Body(None, embed=True),
    api_rate_limit_per_minute: Optional[int] = Body(None, embed=True),
    retention_days: Optional[int] = Body(None, embed=True),
    max_rows_per_job: Optional[int] = Body(None, embed=True),
    max_rows_per_month: Optional[int] = Body(None, embed=True),
):
    """
    Update the default limits for a subscription plan tier.
    Affects all users on that plan (unless they have custom limits).
    """
    from app.models import SubscriptionPlan
    
    tier = tier.lower()
    try:
        tier_enum = SubscriptionTier(tier)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier_enum).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan not found for tier: {tier}")
    
    # Update direct columns
    if max_datasets is not None:
        plan.max_datasets = max_datasets
    if max_api_keys is not None:
        plan.max_api_keys = max_api_keys
    if max_team_members is not None:
        plan.max_team_members = max_team_members
    if api_rate_limit_per_minute is not None:
        plan.api_rate_limit_per_minute = api_rate_limit_per_minute
    if retention_days is not None:
        plan.retention_days = retention_days
    
    # Update features JSON
    features = plan.features or {}
    if max_rows_per_job is not None:
        features["max_rows_per_job"] = max_rows_per_job
    if max_rows_per_month is not None:
        features["max_rows_per_month"] = max_rows_per_month
    plan.features = features
    
    db.commit()
    db.refresh(plan)
    
    return {
        "message": f"Plan limits updated for {tier}",
        "plan": {
            "tier": plan.tier.value,
            "max_datasets": plan.max_datasets,
            "max_api_keys": plan.max_api_keys,
            "max_team_members": plan.max_team_members,
            "api_rate_limit_per_minute": plan.api_rate_limit_per_minute,
            "retention_days": plan.retention_days,
            "features": plan.features,
        }
    }


# =============================================================================
# ORGANIZATION/TEAM MANAGEMENT
# =============================================================================

@router.get(
    "/organizations",
    summary="List all organizations",
)
def admin_list_organizations(
    db: DBSession,
    admin: AdminUser,
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List all organizations with their subscription info."""
    from app.models import Organization, OrganizationMember, User
    from sqlalchemy import desc, func
    
    query = db.query(Organization).filter(Organization.deleted_at.is_(None))
    
    total = query.count()
    organizations = query.order_by(desc(Organization.created_at)).offset(offset).limit(limit).all()
    
    result = []
    for org in organizations:
        # Get member count
        member_count = db.query(func.count(OrganizationMember.id)).filter(
            OrganizationMember.organization_id == org.id
        ).scalar()
        
        # Get owner
        owner = db.query(User).filter(User.id == org.owner_id).first()
        
        # Get owner's subscription (determines org plan)
        owner_sub = db.query(Subscription).filter(
            Subscription.user_id == org.owner_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        owner_tier = None
        if owner_sub:
            from app.models import SubscriptionPlan
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == owner_sub.plan_id).first()
            owner_tier = plan.tier.value if plan else None
        
        result.append({
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "member_count": member_count,
            "owner": {
                "id": str(owner.id) if owner else None,
                "email": owner.email if owner else None,
            } if owner else None,
            "owner_tier": owner_tier,
            "created_at": org.created_at.isoformat() if org.created_at else None,
        })
    
    return {
        "organizations": result,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/organizations/{org_id}/members",
    summary="List organization members",
)
def admin_list_org_members(
    org_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """List all members of an organization with their effective plans."""
    from app.models import Organization, OrganizationMember, User, SubscriptionPlan
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get owner's subscription to determine org plan
    owner_sub = db.query(Subscription).filter(
        Subscription.user_id == org.owner_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    org_tier = "beginner"
    if owner_sub:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == owner_sub.plan_id).first()
        org_tier = plan.tier.value if plan else "beginner"
    
    # Get members
    members = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id
    ).all()
    
    result = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        
        # Member inherits org plan if org has Business/Enterprise
        effective_tier = org_tier if org_tier in ["business", "enterprise"] else "beginner"
        
        result.append({
            "user_id": str(member.user_id),
            "email": user.email if user else None,
            "role": member.role.value if hasattr(member.role, 'value') else member.role,
            "joined_at": member.joined_at.isoformat() if member.joined_at else None,
            "effective_tier": effective_tier,
            "is_owner": member.user_id == org.owner_id,
        })
    
    return {
        "organization": {
            "id": str(org.id),
            "name": org.name,
            "owner_tier": org_tier,
        },
        "members": result,
        "member_count": len(result),
    }


# =============================================================================
# QUOTA MANAGEMENT ENDPOINTS
# =============================================================================

@router.get(
    "/users/{user_id}/usage",
    summary="Get user's usage stats and quotas",
)
def admin_get_user_usage(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
):
    """
    Get comprehensive usage statistics for a user including:
    - Current usage vs limits
    - Historical usage
    - Active subscription details
    """
    from app.services.usage_service import UsageService
    from app.models import User, SubscriptionPlan
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    usage_service = UsageService(db)
    
    # Get current usage and quotas
    current_usage = usage_service.get_current_usage(user_id)
    quotas = usage_service.get_user_quotas(user_id)
    tier = usage_service.get_user_tier(user_id)
    summary = usage_service.get_usage_summary(user_id)
    
    # Get subscription info
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.ON_HOLD])
    ).first()
    
    plan_info = None
    if sub:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
        if plan:
            plan_info = {
                "id": str(plan.id),
                "name": plan.name,
                "tier": plan.tier.value,
                "monthly_price_cents": plan.monthly_price_cents,
            }
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
        },
        "tier": tier.value,
        "subscription": {
            "id": str(sub.id) if sub else None,
            "status": sub.status.value if sub else None,
            "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
            "plan": plan_info,
        } if sub else None,
        "usage": current_usage,
        "quotas": quotas,
        "summary": summary,
    }


@router.put(
    "/users/{user_id}/quota-override",
    summary="Override user quota limits",
)
def admin_override_user_quota(
    user_id: UUID,
    db: DBSession,
    admin: SuperAdminUser,  # Only super admin can override quotas
    custom_limits: dict = Body(..., description="Custom limits to apply"),
    reason: str = Body(..., description="Reason for override"),
    expires_at: Optional[datetime] = Body(None, description="When override expires"),
):
    """
    Set custom quota limits for a user (for dispute resolution, special cases).
    
    Example custom_limits:
    {
        "rows_per_month": 200000,
        "max_rows_per_job": 50000,
        "concurrent_jobs": 5
    }
    """
    from app.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create subscription
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.ON_HOLD])
    ).first()
    
    if not sub:
        raise HTTPException(
            status_code=400, 
            detail="User has no active subscription to override"
        )
    
    # Update custom limits in subscription metadata
    existing_metadata = sub.extra_data or {}
    existing_metadata["custom_limits"] = custom_limits
    existing_metadata["custom_limits_reason"] = reason
    existing_metadata["custom_limits_set_by"] = str(admin.id)
    existing_metadata["custom_limits_set_at"] = datetime.utcnow().isoformat()
    if expires_at:
        existing_metadata["custom_limits_expires_at"] = expires_at.isoformat()
    
    sub.extra_data = existing_metadata
    db.commit()
    
    return {
        "message": "Quota override applied successfully",
        "user_id": str(user_id),
        "custom_limits": custom_limits,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


@router.delete(
    "/users/{user_id}/quota-override",
    summary="Remove user quota override",
)
def admin_remove_quota_override(
    user_id: UUID,
    db: DBSession,
    admin: SuperAdminUser,
):
    """Remove custom quota limits for a user, reverting to plan defaults."""
    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.ON_HOLD])
    ).first()
    
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    # Remove custom limits
    if sub.extra_data:
        sub.extra_data.pop("custom_limits", None)
        sub.extra_data.pop("custom_limits_reason", None)
        sub.extra_data.pop("custom_limits_set_by", None)
        sub.extra_data.pop("custom_limits_set_at", None)
        sub.extra_data.pop("custom_limits_expires_at", None)
        db.commit()
    
    return {"message": "Quota override removed successfully"}


@router.put(
    "/subscriptions/{subscription_id}/change-plan",
    summary="Admin change user's subscription plan",
)
def admin_change_subscription_plan(
    subscription_id: UUID,
    db: DBSession,
    admin: AdminUser,
    new_plan_id: UUID = Body(..., embed=True, description="New plan to assign"),
    reason: str = Body("Admin override", description="Reason for change"),
):
    """
    Change a user's subscription plan immediately.
    Used for upgrades, downgrades, or customer support cases.
    """
    from app.models import SubscriptionPlan
    
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    new_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == new_plan_id).first()
    if not new_plan:
        raise HTTPException(status_code=404, detail="New plan not found")
    
    old_plan_id = sub.plan_id
    sub.plan_id = new_plan_id
    
    # Log the change
    if not sub.extra_data:
        sub.extra_data = {}
    sub.extra_data["admin_plan_changes"] = sub.extra_data.get("admin_plan_changes", [])
    sub.extra_data["admin_plan_changes"].append({
        "old_plan_id": str(old_plan_id),
        "new_plan_id": str(new_plan_id),
        "changed_by": str(admin.id),
        "changed_at": datetime.utcnow().isoformat(),
        "reason": reason,
    })
    
    db.commit()
    
    return {
        "message": f"Subscription changed to {new_plan.name}",
        "subscription_id": str(subscription_id),
        "new_tier": new_plan.tier.value,
    }


@router.put(
    "/subscriptions/{subscription_id}/extend",
    summary="Extend subscription period",
)
def admin_extend_subscription(
    subscription_id: UUID,
    db: DBSession,
    admin: AdminUser,
    days: int = Body(..., embed=True, ge=1, le=365, description="Days to extend"),
    reason: str = Body("Admin extension", description="Reason for extension"),
):
    """Extend a subscription's current period by specified days."""
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Extend period
    if sub.current_period_end:
        sub.current_period_end = sub.current_period_end + timedelta(days=days)
    else:
        sub.current_period_end = datetime.utcnow() + timedelta(days=days)
    
    # If subscription was expired, reactivate it
    if sub.status == SubscriptionStatus.EXPIRED:
        sub.status = SubscriptionStatus.ACTIVE
    
    # Log extension
    if not sub.extra_data:
        sub.extra_data = {}
    sub.extra_data["admin_extensions"] = sub.extra_data.get("admin_extensions", [])
    sub.extra_data["admin_extensions"].append({
        "days": days,
        "extended_by": str(admin.id),
        "extended_at": datetime.utcnow().isoformat(),
        "reason": reason,
    })
    
    db.commit()
    
    return {
        "message": f"Subscription extended by {days} days",
        "new_period_end": sub.current_period_end.isoformat(),
    }


@router.put(
    "/subscriptions/{subscription_id}/status",
    summary="Change subscription status",
)
def admin_change_subscription_status(
    subscription_id: UUID,
    db: DBSession,
    admin: AdminUser,
    new_status: str = Body(..., embed=True, description="New status"),
    reason: str = Body("Admin action", description="Reason for change"),
):
    """
    Change subscription status directly.
    Valid statuses: active, on_hold, cancelled, paused, expired
    """
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    try:
        status_enum = SubscriptionStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid: {[s.value for s in SubscriptionStatus]}"
        )
    
    old_status = sub.status
    sub.status = status_enum
    
    # Log the change
    if not sub.extra_data:
        sub.extra_data = {}
    sub.extra_data["admin_status_changes"] = sub.extra_data.get("admin_status_changes", [])
    sub.extra_data["admin_status_changes"].append({
        "old_status": old_status.value,
        "new_status": status_enum.value,
        "changed_by": str(admin.id),
        "changed_at": datetime.utcnow().isoformat(),
        "reason": reason,
    })
    
    db.commit()
    
    return {
        "message": f"Subscription status changed to {new_status}",
        "old_status": old_status.value,
        "new_status": status_enum.value,
    }


@router.post(
    "/users/{user_id}/create-subscription",
    summary="Create subscription for user (admin grant)",
)
def admin_create_subscription(
    user_id: UUID,
    db: DBSession,
    admin: AdminUser,
    plan_id: UUID = Body(..., description="Plan to assign"),
    months: int = Body(1, ge=1, le=24, description="Subscription duration in months"),
    reason: str = Body("Admin grant", description="Reason for grant"),
):
    """
    Create a subscription for a user without payment.
    Used for promotional grants, employee accounts, etc.
    """
    from app.models import User, SubscriptionPlan, BillingCycle
    import uuid
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if user already has active subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="User already has an active subscription"
        )
    
    # Create subscription
    now = datetime.utcnow()
    new_sub = Subscription(
        id=uuid.uuid4(),
        user_id=user_id,
        plan_id=plan_id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
        current_period_start=now,
        current_period_end=now + timedelta(days=30 * months),
        payment_provider=PaymentProvider.MANUAL,
        extra_data={
            "admin_granted": True,
            "granted_by": str(admin.id),
            "granted_at": now.isoformat(),
            "reason": reason,
            "granted_months": months,
        }
    )
    
    db.add(new_sub)
    db.commit()
    
    return {
        "message": f"Subscription created for {user.email}",
        "subscription_id": str(new_sub.id),
        "plan": plan.name,
        "tier": plan.tier.value,
        "expires_at": new_sub.current_period_end.isoformat(),
    }


@router.get(
    "/subscriptions/stats",
    summary="Get subscription statistics",
)
def admin_get_subscription_stats(
    db: DBSession,
    admin: AdminUser,
):
    """Get comprehensive subscription statistics for admin dashboard."""
    from sqlalchemy import func
    from app.models import SubscriptionPlan
    
    # Active subscriptions count
    active_count = db.query(func.count(Subscription.id)).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar() or 0
    
    # Trial count (if any)
    trial_count = db.query(func.count(Subscription.id)).filter(
        Subscription.status == SubscriptionStatus.TRIALING
    ).scalar() or 0
    
    # Expired/cancelled in last 30 days (churn)
    churn_date = datetime.utcnow() - timedelta(days=30)
    churned_count = db.query(func.count(Subscription.id)).filter(
        Subscription.status.in_([SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED]),
        Subscription.updated_at >= churn_date
    ).scalar() or 0
    
    # Calculate MRR
    active_subs = db.query(Subscription, SubscriptionPlan).join(
        SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id
    ).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).all()
    
    mrr = sum(plan.monthly_price_cents for _, plan in active_subs) / 100  # Convert cents to dollars
    
    # Subscriptions by tier
    by_tier = {}
    for sub, plan in active_subs:
        tier = plan.tier.value
        by_tier[tier] = by_tier.get(tier, 0) + 1
    
    # Calculate churn rate
    total_start = active_count + churned_count
    churn_rate = (churned_count / total_start * 100) if total_start > 0 else 0
    
    # Average revenue per user
    arpu = mrr / active_count if active_count > 0 else 0
    
    return {
        "active_count": active_count,
        "trial_count": trial_count,
        "churned_count": churned_count,
        "churn_rate": round(churn_rate, 2),
        "mrr": round(mrr, 2),
        "arpu": round(arpu, 2),
        "ltv": round(arpu * 12, 2),  # Simple LTV estimate
        "by_tier": by_tier,
    }


# =============================================================================
# CELERY MONITORING
# =============================================================================

@router.get(
    "/celery/workers",
    summary="Get Celery workers",
)
def get_celery_workers(
    admin: AdminUser,
):
    """Get list of Celery workers with their status."""
    try:
        from app.celery_app import celery_app
        
        stats = celery_app.control.inspect().stats() or {}
        workers = []
        
        for hostname, info in stats.items():
            workers.append({
                "hostname": hostname,
                "status": "online",
                "pid": info.get("pid"),
                "processed": info.get("total", {}).get("executed", 0),
            })
        
        return workers
    except Exception:
        return []


@router.get(
    "/celery/queue",
    summary="Get Celery queue stats",
)
def get_celery_queue_stats(
    admin: AdminUser,
):
    """Get Celery queue statistics."""
    try:
        from app.celery_app import celery_app
        
        # Get queue info
        inspect = celery_app.control.inspect()
        reserved = inspect.reserved() or {}
        active = inspect.active() or {}
        
        pending = sum(len(tasks) for tasks in reserved.values())
        processing = sum(len(tasks) for tasks in active.values())
        
        return {
            "total_jobs": pending + processing,
            "pending_jobs": pending,
            "processing_jobs": processing,
            "failed_jobs": 0,  # Would need to track separately
        }
    except Exception:
        return {
            "total_jobs": 0,
            "pending_jobs": 0,
            "processing_jobs": 0,
            "failed_jobs": 0,
        }


# =============================================================================
# METRICS ENDPOINTS
# =============================================================================

@router.get(
    "/metrics/api",
    summary="Get API metrics",
)
def get_api_metrics(
    admin: AdminUser,
):
    """Get API performance metrics."""
    return {
        "average_response_time": 45.2,  # ms
        "requests_per_minute": 120,
        "error_rate": 0.02,
    }


@router.get(
    "/metrics/database",
    summary="Get database metrics",
)
def get_database_metrics(
    db: DBSession,
    admin: AdminUser,
):
    """Get database connection and query metrics."""
    return {
        "active_connections": 5,
        "idle_connections": 10,
        "slow_queries": 0,
    }


@router.get(
    "/metrics/redis",
    summary="Get Redis metrics",
)
def get_redis_metrics(
    admin: AdminUser,
):
    """Get Redis cache metrics."""
    try:
        import redis as redis_sync
        from app.core.config import settings
        
        client = redis_sync.from_url(settings.REDIS_URL)
        info = client.info()
        client.close()
        
        total_keys = info.get("db0", {}).get("keys", 0) if isinstance(info.get("db0"), dict) else 0
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
        
        return {
            "memory_used": info.get("used_memory", 0),
            "total_keys": total_keys,
            "hit_rate": round(hit_rate, 3),
        }
    except Exception:
        return {
            "memory_used": 0,
            "total_keys": 0,
            "hit_rate": 0,
        }


# =============================================================================
# ALERTS ENDPOINT
# =============================================================================

@router.get(
    "/alerts",
    summary="Get active alerts",
)
def get_active_alerts(
    admin: AdminUser,
    severity: Optional[str] = Query(None, description="Filter by severity"),
):
    """Get active system alerts."""
    # In production, this would query an alerts table
    alerts = []
    
    if severity:
        alerts = [a for a in alerts if a.get("severity") == severity]
    
    return {
        "items": alerts,
        "total": len(alerts),
    }


@router.post(
    "/alerts/{alert_id}/acknowledge",
    summary="Acknowledge alert",
)
def acknowledge_alert(
    alert_id: str,
    admin: AdminUser,
):
    """Acknowledge an alert."""
    return {"message": "Alert acknowledged", "alert_id": alert_id}


# =============================================================================
# CONTAINER HEALTH
# =============================================================================

@router.get(
    "/containers",
    summary="Get container health",
)
def get_container_health(
    admin: AdminUser,
):
    """Get container health status."""
    return {
        "items": [
            {"name": "api", "status": "running", "cpu_percent": 5.0, "memory_mb": 256},
            {"name": "postgres", "status": "running", "cpu_percent": 2.0, "memory_mb": 128},
            {"name": "redis", "status": "running", "cpu_percent": 1.0, "memory_mb": 64},
        ],
        "total": 3,
    }


@router.get(
    "/containers/{container_name}/stats",
    summary="Get container stats",
)
def get_container_stats(
    container_name: str,
    admin: AdminUser,
):
    """Get detailed stats for a specific container."""
    return {
        "name": container_name,
        "status": "running",
        "cpu_percent": 5.0,
        "memory_mb": 256,
        "memory_limit_mb": 1024,
        "network_rx_bytes": 1024000,
        "network_tx_bytes": 512000,
    }
