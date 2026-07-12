"""
Admin schemas for Synthesize.io API.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# DASHBOARD & ANALYTICS SCHEMAS
# =============================================================================

class AdminDashboardStats(BaseSchema):
    """Admin dashboard statistics."""
    
    # User stats
    total_users: int = 0
    active_users_today: int = 0
    active_users_week: int = 0
    active_users_month: int = 0
    new_users_today: int = 0
    new_users_week: int = 0
    new_users_month: int = 0
    
    # Organization stats
    total_organizations: int = 0
    new_organizations_month: int = 0
    
    # Subscription stats
    total_subscriptions: int = 0
    paid_subscriptions: int = 0
    trial_subscriptions: int = 0
    churned_this_month: int = 0
    
    # Revenue stats
    mrr: Decimal = Decimal("0")  # Monthly recurring revenue
    arr: Decimal = Decimal("0")  # Annual recurring revenue
    revenue_this_month: Decimal = Decimal("0")
    
    # Usage stats
    total_datasets: int = 0
    total_rows_generated: int = 0
    rows_generated_today: int = 0
    rows_generated_month: int = 0
    total_jobs: int = 0
    jobs_today: int = 0
    active_jobs: int = 0
    failed_jobs_today: int = 0
    
    # API stats
    api_calls_today: int = 0
    api_calls_month: int = 0
    average_response_time_ms: float = 0.0
    
    # Storage stats
    total_storage_bytes: int = 0


class AdminChartDataPoint(BaseSchema):
    """Data point for admin charts."""
    
    date: datetime
    value: float
    label: Optional[str] = None


class AdminChartResponse(BaseSchema):
    """Chart data for admin analytics."""
    
    chart_type: str
    title: str
    data_points: list[AdminChartDataPoint]
    total: Optional[float] = None
    change_percentage: Optional[float] = None


# =============================================================================
# USER MANAGEMENT SCHEMAS
# =============================================================================

class AdminUserCreate(BaseSchema):
    """Admin create user."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    status: str = "active"
    email_verified: bool = False
    send_welcome_email: bool = True


class AdminUserUpdate(BaseSchema):
    """Admin update user."""
    
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    email_verified: Optional[bool] = None


class AdminUserResponse(BaseSchema, TimestampMixin):
    """Admin user response with full details."""
    
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    email_verified: bool
    last_login_at: Optional[datetime]
    login_count: int
    
    # Subscription info
    subscription_plan: Optional[str]
    subscription_status: Optional[str]
    
    # Usage info
    datasets_count: int = 0
    jobs_count: int = 0
    api_calls_count: int = 0


class AdminUserListResponse(PaginatedResponse[AdminUserResponse]):
    """Paginated admin user list."""
    pass


class AdminUserDetailResponse(AdminUserResponse):
    """Detailed admin user view."""
    
    organizations: list[dict] = []
    subscriptions: list[dict] = []
    api_keys: list[dict] = []
    recent_activity: list[dict] = []


# =============================================================================
# SUBSCRIPTION MANAGEMENT SCHEMAS
# =============================================================================

class AdminSubscriptionUpdate(BaseSchema):
    """Admin update subscription."""
    
    plan_id: Optional[UUID] = None
    status: Optional[str] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    notes: Optional[str] = None


class AdminSubscriptionResponse(BaseSchema, TimestampMixin):
    """Admin subscription view."""
    
    id: UUID
    user_id: UUID
    user_email: str
    organization_id: Optional[UUID]
    plan_id: UUID
    plan_name: str
    status: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: Optional[datetime]
    
    # Usage
    rows_used: int
    rows_limit: int
    
    # Revenue
    total_paid: Decimal = Decimal("0")


class AdminSubscriptionListResponse(PaginatedResponse[AdminSubscriptionResponse]):
    """Paginated admin subscription list."""
    pass


# =============================================================================
# PLAN MANAGEMENT SCHEMAS
# =============================================================================

class AdminPlanCreate(BaseSchema):
    """Create subscription plan."""
    
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    price_monthly: Decimal = Field(..., ge=0)
    price_yearly: Decimal = Field(..., ge=0)
    currency: str = "USD"
    features: dict[str, Any]
    sort_order: int = 0
    is_active: bool = True


class AdminPlanUpdate(BaseSchema):
    """Update subscription plan."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = Field(None, ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    features: Optional[dict[str, Any]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# =============================================================================
# SYSTEM CONFIGURATION SCHEMAS
# =============================================================================

class SystemConfigUpdate(BaseSchema):
    """Update system configuration."""
    
    value: Any
    description: Optional[str] = None


class SystemConfigResponse(BaseSchema, TimestampMixin):
    """System configuration."""
    
    id: UUID
    key: str
    value: Any
    value_type: str
    category: str
    description: Optional[str]
    is_public: bool
    updated_by: Optional[UUID]


class SystemConfigListResponse(BaseSchema):
    """List of system configs."""
    
    configs: list[SystemConfigResponse]


# =============================================================================
# FEATURE FLAG SCHEMAS
# =============================================================================

class FeatureFlagCreate(BaseSchema):
    """Create feature flag."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_enabled: bool = False
    rollout_percentage: int = Field(0, ge=0, le=100)
    allowed_users: list[UUID] = []
    allowed_plans: list[str] = []


class FeatureFlagUpdate(BaseSchema):
    """Update feature flag."""
    
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)
    allowed_users: Optional[list[UUID]] = None
    allowed_plans: Optional[list[str]] = None


class FeatureFlagResponse(BaseSchema, TimestampMixin):
    """Feature flag."""
    
    id: UUID
    name: str
    description: Optional[str]
    is_enabled: bool
    rollout_percentage: int
    allowed_users: list[UUID]
    allowed_plans: list[str]


class FeatureFlagListResponse(BaseSchema):
    """List of feature flags."""
    
    flags: list[FeatureFlagResponse]


# =============================================================================
# AUDIT LOG SCHEMAS
# =============================================================================

class AuditLogResponse(BaseSchema):
    """Audit log entry."""
    
    id: UUID
    user_id: Optional[UUID]
    user_email: Optional[str]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    old_values: Optional[dict]
    new_values: Optional[dict]
    user_agent: Optional[str]
    created_at: datetime


class AuditLogListResponse(PaginatedResponse[AuditLogResponse]):
    """Paginated audit logs."""
    pass


# =============================================================================
# SUPPORT TICKET SCHEMAS
# =============================================================================

class AdminTicketResponse(BaseSchema, TimestampMixin):
    """Admin support ticket view."""
    
    id: UUID
    ticket_number: str
    user_id: UUID
    user_email: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_to: Optional[UUID]
    assigned_to_name: Optional[str]
    resolved_at: Optional[datetime]
    messages_count: int = 0


class AdminTicketListResponse(PaginatedResponse[AdminTicketResponse]):
    """Paginated admin ticket list."""
    pass


class AdminTicketUpdate(BaseSchema):
    """Admin update ticket."""
    
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    internal_notes: Optional[str] = None


class AdminTicketReplyRequest(BaseSchema):
    """Admin reply to ticket."""
    
    message: str = Field(..., min_length=1, max_length=10000)
    is_internal: bool = False


# =============================================================================
# JOB MANAGEMENT SCHEMAS
# =============================================================================

class AdminJobResponse(BaseSchema, TimestampMixin):
    """Admin job view."""
    
    id: UUID
    dataset_id: UUID
    dataset_name: str
    user_id: UUID
    user_email: str
    status: str
    row_count: int
    rows_generated: int
    output_format: str
    priority: str
    progress: float
    error_message: Optional[str]
    worker_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class AdminJobListResponse(PaginatedResponse[AdminJobResponse]):
    """Paginated admin job list."""
    pass


class AdminJobAction(BaseSchema):
    """Admin job action."""
    
    action: str = Field(..., pattern="^(cancel|retry|prioritize)$")
    reason: Optional[str] = None


# =============================================================================
# SYSTEM HEALTH SCHEMAS
# =============================================================================

class ServiceHealth(BaseSchema):
    """Individual service health."""
    
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: Optional[float] = None
    last_check: datetime
    error: Optional[str] = None


class SystemHealthResponse(BaseSchema):
    """System health status."""
    
    status: str  # healthy, degraded, unhealthy
    database: str = "unknown"
    redis: str = "unknown"
    celery: str = "unknown"
    storage: str = "unknown"
    timestamp: Optional[datetime] = None
    
    # Resource usage (optional)
    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    
    # Queue stats (optional)
    pending_jobs: int = 0
    active_workers: int = 0


# =============================================================================
# BULK OPERATIONS SCHEMAS
# =============================================================================

class BulkUserAction(BaseSchema):
    """Bulk user action."""
    
    user_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern="^(activate|deactivate|delete|verify_email|send_password_reset)$")
    reason: Optional[str] = None


class BulkActionResponse(BaseSchema):
    """Bulk action result."""
    
    total: int
    successful: int
    failed: int
    errors: list[dict] = []


# =============================================================================
# ADDITIONAL ENDPOINT SCHEMAS
# =============================================================================

class DashboardStatsResponse(BaseSchema):
    """Dashboard statistics."""
    
    total_users: int = 0
    active_users: int = 0
    new_users_today: int = 0
    new_users_this_week: int = 0
    new_users_this_month: int = 0
    total_subscriptions: int = 0
    active_subscriptions: int = 0
    mrr: float = 0.0
    arr: float = 0.0
    total_revenue: float = 0.0
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_rows_generated: int = 0
    total_api_calls: int = 0
    
    # Change percentages (comparing this period vs previous period)
    users_change_pct: float = 0.0
    active_users_change_pct: float = 0.0
    datasets_change_pct: float = 0.0
    jobs_change_pct: float = 0.0
    revenue_change_pct: float = 0.0
    rows_generated_change_pct: float = 0.0
    new_users_week_change_pct: float = 0.0
    
    # Additional stats for dashboard
    total_datasets: int = 0
    revenue_this_month: float = 0.0
    rows_generated_today: int = 0
    avg_job_size: int = 0


class UserManagementAction(BaseSchema):
    """User management action."""
    
    action: str = Field(..., pattern="^(suspend|reactivate|verify_email|reset_password|change_role|delete)$")
    reason: Optional[str] = None
    new_role: Optional[str] = None


class SubscriptionManagementAction(BaseSchema):
    """Subscription management action."""
    
    action: str = Field(..., pattern="^(cancel|extend|upgrade|downgrade|refund)$")
    reason: Optional[str] = None
    days: Optional[int] = None
    new_plan_id: Optional[UUID] = None


class SupportTicketResponse(BaseSchema):
    """Support ticket response for endpoints."""
    
    id: UUID
    ticket_number: str
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    subject: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: str = "normal"
    status: str = "open"
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AnalyticsResponse(BaseSchema):
    """Analytics data response."""
    
    metric: str
    period: str
    data: list[dict] = []

