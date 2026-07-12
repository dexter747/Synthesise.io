"""
Synthesize.io Database Models
============================
Comprehensive SQLAlchemy models for the synthetic data generation platform.

Models organized by domain:
- User & Authentication
- Organizations & Teams
- Subscriptions & Billing
- Data Generation
- Usage & Quotas
- API & Webhooks
- Analytics & Audit
- Admin & System
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Boolean, Text, JSON,
    DateTime, Date, ForeignKey, Index, UniqueConstraint, CheckConstraint,
    Enum, Table
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from app.core.database import Base


# =============================================================================
# ENUMS
# =============================================================================

class UserStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SUPPORT = "support"
    ANALYST = "analyst"


class OAuthProvider(str, PyEnum):
    GOOGLE = "google"
    GITHUB = "github"


class OrganizationRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class SubscriptionTier(str, PyEnum):
    BEGINNER = "beginner"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, PyEnum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    ON_HOLD = "on_hold"  # Dodo Payments status for failed renewals
    CANCELLED = "cancelled"
    TRIALING = "trialing"
    PAUSED = "paused"
    EXPIRED = "expired"
    PENDING = "pending"


class BillingCycle(str, PyEnum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"


class PaymentProvider(str, PyEnum):
    DODO = "dodo"  # Dodo Payments - primary payment provider
    MANUAL = "manual"  # Manual/admin-applied payments


class JobStatus(str, PyEnum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMEOUT = "timeout"


class JobPriority(str, PyEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class DatasetStatus(str, PyEnum):
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    EXPIRED = "expired"
    DELETED = "deleted"
    FAILED = "failed"


class DataFormat(str, PyEnum):
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    SQL = "sql"
    PARQUET = "parquet"
    EXCEL = "excel"


class WebhookEvent(str, PyEnum):
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    DATASET_READY = "dataset.ready"
    DATASET_EXPIRED = "dataset.expired"
    QUOTA_WARNING = "quota.warning"
    QUOTA_EXCEEDED = "quota.exceeded"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"


class NotificationType(str, PyEnum):
    EMAIL = "email"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class QueryStatus(str, PyEnum):
    """Status for customer contact queries"""
    NEW = "new"
    READ = "read"
    RESPONDED = "responded"
    CLOSED = "closed"


class AuditAction(str, PyEnum):
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    USER_PASSWORD_RESET = "user.password_reset"
    USER_PROFILE_UPDATE = "user.profile_update"
    USER_DELETE = "user.delete"
    
    # Data actions
    DATASET_CREATE = "dataset.create"
    DATASET_DELETE = "dataset.delete"
    DATASET_DOWNLOAD = "dataset.download"
    DATASET_SHARE = "dataset.share"
    
    # API actions
    API_KEY_CREATE = "api_key.create"
    API_KEY_REVOKE = "api_key.revoke"
    
    # Billing actions
    SUBSCRIPTION_CREATE = "subscription.create"
    SUBSCRIPTION_UPDATE = "subscription.update"
    SUBSCRIPTION_CANCEL = "subscription.cancel"
    PAYMENT_CREATE = "payment.create"
    REFUND_CREATE = "refund.create"
    
    # Admin actions
    ADMIN_USER_UPDATE = "admin.user_update"
    ADMIN_USER_SUSPEND = "admin.user_suspend"
    ADMIN_USER_IMPERSONATE = "admin.user_impersonate"
    ADMIN_CONFIG_UPDATE = "admin.config_update"
    ADMIN_JOB_RETRY = "admin.job_retry"
    ADMIN_JOB_CANCEL = "admin.job_cancel"


# =============================================================================
# BASE MIXIN
# =============================================================================

class TimestampMixin:
    """Adds created_at and updated_at columns"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """Adds soft delete capability"""
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)


# =============================================================================
# USER & AUTHENTICATION
# =============================================================================

class User(Base, TimestampMixin, SoftDeleteMixin):
    """Core user model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en")
    
    # Status & Role
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Organization - track user's currently active organization
    active_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    # Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    
    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    use_case = Column(String(50), nullable=True)  # testing, ml, development, other
    company_name = Column(String(200), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Relationships
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="user", cascade="all, delete-orphan")
    generation_requests = relationship("GenerationRequest", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan", foreign_keys="[AuditLog.user_id]")
    organization_memberships = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan", foreign_keys="[OrganizationMember.user_id]")
    generation_jobs = relationship("GenerationJob", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_users_email_status", "email", "status"),
        Index("idx_users_role", "role"),
        Index("idx_users_created_at", "created_at"),
    )


class OAuthAccount(Base, TimestampMixin):
    """OAuth provider accounts linked to users"""
    __tablename__ = "oauth_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    provider = Column(Enum(OAuthProvider), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    
    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    raw_user_data = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="oauth_accounts")
    
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        Index("idx_oauth_user_id", "user_id"),
    )


class Session(Base, TimestampMixin):
    """User sessions for JWT token management"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255), unique=True, nullable=True, index=True)
    
    device_info = Column(JSON, nullable=True)  # User agent, device type, etc.
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index("idx_sessions_user_active", "user_id", "is_active"),
        Index("idx_sessions_expires", "expires_at"),
    )


class PasswordResetToken(Base, TimestampMixin):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_password_reset_expires", "expires_at"),
    )


class EmailVerificationToken(Base, TimestampMixin):
    """Email verification tokens"""
    __tablename__ = "email_verification_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)  # Email to verify (in case user changes it)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)


# =============================================================================
# ORGANIZATIONS & TEAMS
# =============================================================================

class Organization(Base, TimestampMixin, SoftDeleteMixin):
    """Organizations for team collaboration"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    plan = Column(String(50), default="free")
    status = Column(String(50), default="active")
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    settings = Column(JSON, default=dict)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("OrganizationInvitation", back_populates="organization", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_organizations_owner", "owner_id"),
    )


class OrganizationMember(Base, TimestampMixin):
    """Organization membership"""
    __tablename__ = "organization_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(Enum(OrganizationRole), default=OrganizationRole.MEMBER, nullable=False)
    
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships", foreign_keys=[user_id])
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        Index("idx_org_members_user", "user_id"),
    )


class OrganizationInvitation(Base, TimestampMixin):
    """Pending organization invitations"""
    __tablename__ = "organization_invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    email = Column(String(255), nullable=False)
    role = Column(Enum(OrganizationRole), default=OrganizationRole.MEMBER, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, declined, expired
    
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=True)  # Plain token for comparison (backwards compat)
    token_hash = Column(String(255), unique=True, nullable=True, index=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    declined_at = Column(DateTime(timezone=True), nullable=True)
    
    organization = relationship("Organization", back_populates="invitations")
    invited_by = relationship("User")
    
    __table_args__ = (
        Index("idx_org_invitations_email", "email"),
    )


# =============================================================================
# SUBSCRIPTIONS & BILLING
# =============================================================================

class SubscriptionPlan(Base, TimestampMixin):
    """Subscription plan definitions"""
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    tier = Column(Enum(SubscriptionTier, values_callable=lambda x: [e.value for e in x]), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=True, index=True)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    
    # Pricing (USD only)
    monthly_price_cents = Column(Integer, nullable=False)  # Price in cents (USD)
    annual_price_cents = Column(Integer, nullable=False)
    price_monthly = Column(Integer, nullable=True)  # Alias in dollars
    price_yearly = Column(Integer, nullable=True)  # Alias in dollars
    currency = Column(String(3), default="USD")
    
    # Limits (stored as JSON for flexibility)
    limits = Column(JSON, default=dict)  # {"rows_per_month": 10000, "datasets": 5, ...}
    
    # Legacy limit columns (kept for backward compatibility)
    monthly_data_limit_gb = Column(Float, nullable=True)  # -1 for unlimited
    max_datasets = Column(Integer, default=-1)  # -1 for unlimited
    max_api_keys = Column(Integer, default=5)
    max_team_members = Column(Integer, default=1)
    api_rate_limit_per_minute = Column(Integer, default=60)
    retention_days = Column(Integer, default=30)
    
    # Features (JSON for flexibility)
    features = Column(JSON, default=dict)  # {"api_access": true, "priority_queue": false, ...}
    
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Shown on pricing page
    is_recommended = Column(Boolean, default=False)  # Highlighted plan
    sort_order = Column(Integer, default=0)
    
    # Dodo Payments integration
    dodo_product_id = Column(String(255), nullable=True)  # Dodo product ID (pdt_...)


class Subscription(Base, TimestampMixin):
    """User subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)  # For team plans
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY, nullable=False)
    
    # Billing periods
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Trial
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Dodo Payments references
    dodo_subscription_id = Column(String(255), nullable=True, index=True)  # Dodo subscription ID
    dodo_customer_id = Column(String(255), nullable=True, index=True)  # Dodo customer ID
    dodo_product_id = Column(String(255), nullable=True)  # Dodo product ID (pdt_...)
    payment_provider = Column(Enum(PaymentProvider), default=PaymentProvider.DODO, nullable=True)
    
    # Overrides (for custom Enterprise deals)
    custom_limits = Column(JSON, nullable=True)  # Override plan limits
    discount_percent = Column(Float, default=0)
    
    # Enterprise-specific
    is_enterprise = Column(Boolean, default=False)  # True for custom enterprise deals
    enterprise_contact_id = Column(UUID(as_uuid=True), ForeignKey("enterprise_contact_requests.id"), nullable=True)
    
    extra_data = Column(JSON, default=dict)  # General extra data
    
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan")
    organization = relationship("Organization")
    payments = relationship("Payment", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")
    
    __table_args__ = (
        Index("idx_subscriptions_user_status", "user_id", "status"),
        Index("idx_subscriptions_period_end", "current_period_end"),
        Index("idx_subscriptions_dodo_id", "dodo_subscription_id"),
    )



class Payment(Base, TimestampMixin):
    """Payment transactions"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    provider = Column(Enum(PaymentProvider), default=PaymentProvider.DODO, nullable=False)
    
    # Dodo Payments references
    dodo_payment_id = Column(String(255), nullable=True, index=True)  # Dodo payment ID (pay_...)
    dodo_customer_id = Column(String(255), nullable=True)  # Dodo customer ID
    
    # Payment details
    payment_method_type = Column(String(50), nullable=True)  # card, upi, bank_transfer, etc.
    payment_method_last4 = Column(String(4), nullable=True)
    
    # Failure info
    failure_code = Column(String(100), nullable=True)
    failure_message = Column(Text, nullable=True)
    
    # Refund info
    refunded_amount_cents = Column(Integer, default=0)
    refund_reason = Column(Text, nullable=True)
    
    extra_data = Column(JSON, default=dict)  # Additional payment extra data
    
    # Timestamps
    paid_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User")
    subscription = relationship("Subscription", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")
    
    __table_args__ = (
        Index("idx_payments_user_status", "user_id", "status"),
        Index("idx_payments_dodo_id", "dodo_payment_id"),
        Index("idx_payments_created", "created_at"),
    )


class Coupon(Base, TimestampMixin):
    """Discount coupons for subscriptions"""
    __tablename__ = "coupons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Discount configuration
    discount_type = Column(String(20), default="percentage")  # percentage, fixed_amount
    discount_value = Column(Integer, nullable=False)  # Percentage (0-100) or cents
    
    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Also known as valid_to
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    times_used = Column(Integer, default=0)  # Also known as current_uses
    max_uses_per_user = Column(Integer, nullable=True)
    
    # Restrictions
    min_amount_cents = Column(Integer, nullable=True)  # Minimum purchase amount
    applicable_plans = Column(JSON, default=list)  # List of plan IDs, empty = all plans
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    extra_data = Column(JSON, default=dict)
    
    __table_args__ = (
        Index("idx_coupons_code", "code"),
        Index("idx_coupons_active", "is_active"),
    )
    
    @property
    def is_valid(self) -> bool:
        """Check if coupon is currently valid"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return True


class Invoice(Base, TimestampMixin):
    """Invoices for payments"""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    amount_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, default=0)
    total_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    
    status = Column(String(20), default="draft")  # draft, open, paid, void, uncollectible
    
    # Line items
    line_items = Column(JSON, default=list)  # [{description, quantity, unit_price, amount}]
    
    # Billing info snapshot
    billing_name = Column(String(200), nullable=True)
    billing_email = Column(String(255), nullable=True)
    billing_address = Column(JSON, nullable=True)
    
    # Files
    pdf_url = Column(String(500), nullable=True)
    
    # Dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    user = relationship("User")
    subscription = relationship("Subscription", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")
    
    __table_args__ = (
        Index("idx_invoices_user_status", "user_id", "status"),
    )


# =============================================================================
# DATA GENERATION
# =============================================================================

class GenerationRequest(Base, TimestampMixin, SoftDeleteMixin):
    """Data generation requests from users"""
    __tablename__ = "generation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    # Request details
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)  # Natural language description
    
    # Configuration
    row_count = Column(Integer, nullable=False)
    output_format = Column(Enum(DataFormat), default=DataFormat.CSV, nullable=False)
    
    # LLM processing
    refined_schema = Column(JSON, nullable=True)  # Extracted schema from LLM
    sample_data = Column(JSON, nullable=True)  # LLM-generated sample (10-50 rows)
    llm_response_raw = Column(JSON, nullable=True)  # Raw LLM response for debugging
    
    # Generation settings
    settings = Column(JSON, default=dict)  # Custom settings, seed, etc.
    
    # Status
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    # Cost tracking
    estimated_size_bytes = Column(BigInteger, nullable=True)
    actual_size_bytes = Column(BigInteger, nullable=True)
    llm_tokens_used = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="generation_requests")
    organization = relationship("Organization")
    datasets = relationship("Dataset", back_populates="generation_request")
    jobs = relationship("GenerationJob", back_populates="request")
    
    __table_args__ = (
        Index("idx_gen_requests_user_status", "user_id", "status"),
        Index("idx_gen_requests_created", "created_at"),
    )


class GenerationJob(Base, TimestampMixin):
    """Background jobs for data generation"""
    __tablename__ = "generation_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    request_id = Column(UUID(as_uuid=True), ForeignKey("generation_requests.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    # Celery task tracking
    celery_task_id = Column(String(255), unique=True, nullable=True, index=True)
    
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    priority = Column(Enum(JobPriority), default=JobPriority.NORMAL, nullable=False)
    queue_name = Column(String(50), default="generation")
    
    # Job parameters
    output_format = Column(String(50), default="csv")
    generation_options = Column(JSON, nullable=True)
    
    # Progress tracking
    progress_percent = Column(Float, default=0)
    progress = Column(Float, default=0)  # Alias for progress_percent
    progress_message = Column(String(255), nullable=True)
    rows_generated = Column(Integer, default=0)
    row_count = Column(Integer, default=0)  # Total rows to generate
    
    # Output info
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    
    # LLM usage tracking
    llm_model = Column(String(100), nullable=True)
    llm_tokens_used = Column(Integer, default=0)
    credits_used = Column(Float, default=0)
    
    # Timing
    queued_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Worker info
    worker_id = Column(String(255), nullable=True)
    
    request = relationship("GenerationRequest", back_populates="jobs")
    dataset = relationship("Dataset", foreign_keys=[dataset_id])
    user = relationship("User", back_populates="generation_jobs")
    
    __table_args__ = (
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_queue_priority", "queue_name", "priority", "status"),
        Index("idx_jobs_created", "created_at"),
    )


class Dataset(Base, TimestampMixin, SoftDeleteMixin):
    """Generated datasets"""
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    generation_request_id = Column(UUID(as_uuid=True), ForeignKey("generation_requests.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    # Dataset info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schema and metadata
    schema_definition = Column(JSON, nullable=True)  # Column definitions
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=True)
    
    # File info
    format = Column(Enum(DataFormat), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    file_path = Column(String(500), nullable=True)  # Path on local storage
    file_checksum = Column(String(64), nullable=True)  # SHA-256
    compressed = Column(Boolean, default=False)
    
    # Status
    status = Column(Enum(DatasetStatus), default=DatasetStatus.READY, nullable=False)
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)  # 0-100
    quality_issues = Column(JSON, nullable=True)  # List of detected issues
    
    # Sharing
    is_public = Column(Boolean, default=False)
    share_token = Column(String(64), unique=True, nullable=True, index=True)
    
    # Retention
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tags for organization
    tags = Column(JSON, default=list)
    
    user = relationship("User", back_populates="datasets")
    generation_request = relationship("GenerationRequest", back_populates="datasets")
    organization = relationship("Organization")
    downloads = relationship("DatasetDownload", back_populates="dataset")
    schema_fields = relationship("SchemaField", back_populates="dataset", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_datasets_user_status", "user_id", "status"),
        Index("idx_datasets_expires", "expires_at"),
        Index("idx_datasets_tags", "tags", postgresql_using="gin"),
    )


class SchemaField(Base, TimestampMixin):
    """Individual field definitions for dataset schemas"""
    __tablename__ = "schema_fields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    
    # Field definition
    name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=True)
    data_type = Column(String(50), nullable=False)  # string, integer, float, email, etc.
    
    # Constraints as JSON
    constraints = Column(JSON, default=dict)  # min, max, pattern, nullable, etc.
    
    # LLM guidance for smart generation
    llm_guidance = Column(Text, nullable=True)
    
    # Ordering
    order_index = Column(Integer, default=0)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="schema_fields")
    
    __table_args__ = (
        Index("idx_schema_fields_dataset", "dataset_id"),
        UniqueConstraint("dataset_id", "name", name="uq_schema_field_name"),
    )


class DatasetDownload(Base, TimestampMixin):
    """Track dataset downloads"""
    __tablename__ = "dataset_downloads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for shared link downloads
    
    user_agent = Column(Text, nullable=True)
    
    download_format = Column(Enum(DataFormat), nullable=True)  # If converted on download
    
    dataset = relationship("Dataset", back_populates="downloads")
    
    __table_args__ = (
        Index("idx_downloads_dataset", "dataset_id"),
        Index("idx_downloads_created", "created_at"),
    )


class DataTemplate(Base, TimestampMixin, SoftDeleteMixin):
    """Reusable data generation templates"""
    __tablename__ = "data_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for system templates
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e-commerce, healthcare, finance, etc.
    
    # Template definition
    schema_template = Column(JSON, nullable=False)
    sample_prompt = Column(Text, nullable=True)
    default_settings = Column(JSON, default=dict)
    
    # Visibility
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # Built-in templates
    
    # Stats
    use_count = Column(Integer, default=0)
    
    tags = Column(JSON, default=list)
    
    __table_args__ = (
        Index("idx_templates_category", "category"),
        Index("idx_templates_public", "is_public"),
    )


# =============================================================================
# USAGE & QUOTAS
# =============================================================================

class UsageRecord(Base, TimestampMixin):
    """Daily usage records for quota tracking"""
    __tablename__ = "usage_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    date = Column(Date, nullable=False)
    
    # Usage metrics
    data_generated_bytes = Column(BigInteger, default=0)
    datasets_created = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    llm_tokens_used = Column(Integer, default=0)
    
    # Costs (in cents)
    llm_cost_cents = Column(Integer, default=0)
    storage_cost_cents = Column(Integer, default=0)
    
    user = relationship("User", back_populates="usage_records")
    
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_usage_user_date"),
        Index("idx_usage_user_date", "user_id", "date"),
    )


class UsageAlert(Base, TimestampMixin):
    """Usage alerts sent to users"""
    __tablename__ = "usage_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)  # quota_80, quota_100, rate_limit
    threshold_percent = Column(Float, nullable=True)
    
    message = Column(Text, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_alerts_user", "user_id"),
    )


# =============================================================================
# API & WEBHOOKS
# =============================================================================

class APIKey(Base, TimestampMixin, SoftDeleteMixin):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for identification
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Permissions (optional, for fine-grained access)
    scopes = Column(JSON, default=list)  # ["read:datasets", "write:generate"]
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)  # Override default
    ip_whitelist = Column(JSON, default=list)  # IP addresses allowed to use this key
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage stats
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_ip = Column(String(45), nullable=True)  # IPv6 max length
    total_requests = Column(Integer, default=0)
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        Index("idx_api_keys_user", "user_id"),
    )


class APIRequestLog(Base):
    """API request logs for analytics and debugging"""
    __tablename__ = "api_request_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    query_params = Column(JSON, nullable=True)
    
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    
    user_agent = Column(Text, nullable=True)
    
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index("idx_api_logs_timestamp", "timestamp"),
        Index("idx_api_logs_user", "user_id", "timestamp"),
        Index("idx_api_logs_path", "path", "timestamp"),
    )


class Webhook(Base, TimestampMixin, SoftDeleteMixin):
    """Webhook configurations"""
    __tablename__ = "webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)  # For HMAC signature
    
    events = Column(JSON, nullable=False)  # List of WebhookEvent values
    headers = Column(JSON, nullable=True)  # Custom headers
    retry_config = Column(JSON, nullable=True)  # Retry configuration
    
    is_active = Column(Boolean, default=True)
    
    # Health tracking
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook")
    
    __table_args__ = (
        Index("idx_webhooks_user", "user_id"),
    )


class WebhookDelivery(Base, TimestampMixin):
    """Webhook delivery attempts"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    
    # Delivery status
    status = Column(String(20), nullable=False)  # pending, success, failed
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    attempt_count = Column(Integer, default=1)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    webhook = relationship("Webhook", back_populates="deliveries")
    
    __table_args__ = (
        Index("idx_webhook_deliveries_webhook", "webhook_id"),
        Index("idx_webhook_deliveries_status", "status"),
    )


# =============================================================================
# NOTIFICATIONS
# =============================================================================

class Notification(Base, TimestampMixin):
    """In-app notifications"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(String(50), nullable=False)  # job_complete, quota_warning, payment_failed, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    data = Column(JSON, nullable=True)  # Additional context
    action_url = Column(String(500), nullable=True)  # Link to relevant page
    
    read_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "read_at"),
        Index("idx_notifications_created", "created_at"),
    )


class EmailLog(Base, TimestampMixin):
    """Email sending log"""
    __tablename__ = "email_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    to_email = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    
    subject = Column(String(500), nullable=False)
    template_name = Column(String(100), nullable=True)
    
    status = Column(String(20), nullable=False)  # queued, sent, failed, bounced
    
    error_message = Column(Text, nullable=True)
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_email_logs_user", "user_id"),
        Index("idx_email_logs_status", "status"),
    )


# =============================================================================
# AUDIT & ANALYTICS
# =============================================================================

class AuditLog(Base, TimestampMixin):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # For admin actions
    
    action = Column(String(100), nullable=False)  # AuditAction value
    resource_type = Column(String(50), nullable=True)  # user, dataset, subscription, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Context
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)  # For tracing
    
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])
    
    __table_args__ = (
        Index("idx_audit_logs_user", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created", "created_at"),
    )


class AnalyticsEvent(Base):
    """Custom analytics events (beyond Google Analytics)"""
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    event_name = Column(String(100), nullable=False)
    event_category = Column(String(50), nullable=True)
    
    properties = Column(JSON, default=dict)
    
    # Attribution
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Context
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_events_user", "user_id"),
        Index("idx_events_name", "event_name"),
        Index("idx_events_timestamp", "timestamp"),
    )


# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

class SystemConfig(Base, TimestampMixin):
    """System-wide configuration settings"""
    __tablename__ = "system_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    
    description = Column(Text, nullable=True)
    is_secret = Column(Boolean, default=False)  # Mask in UI
    
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class FeatureFlag(Base, TimestampMixin):
    """Feature flags for gradual rollouts"""
    __tablename__ = "feature_flags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    is_enabled = Column(Boolean, default=False)
    
    # Targeting
    enabled_for_users = Column(JSON, default=list)  # Specific user IDs
    enabled_for_tiers = Column(JSON, default=list)  # Subscription tiers
    rollout_percentage = Column(Float, default=0)  # 0-100
    
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class MaintenanceWindow(Base, TimestampMixin):
    """Scheduled maintenance windows"""
    __tablename__ = "maintenance_windows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    
    is_active = Column(Boolean, default=False)
    affected_services = Column(JSON, default=list)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


# =============================================================================
# SUPPORT
# =============================================================================

class SupportTicket(Base, TimestampMixin):
    """Support tickets"""
    __tablename__ = "support_tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # billing, technical, general, feature_request
    
    status = Column(String(20), default="open")  # open, in_progress, waiting, resolved, closed
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    
    tags = Column(JSON, default=list)
    
    user = relationship("User", foreign_keys=[user_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    messages = relationship("SupportMessage", back_populates="ticket")
    
    __table_args__ = (
        Index("idx_tickets_user_status", "user_id", "status"),
        Index("idx_tickets_assigned", "assigned_to_id", "status"),
    )


class SupportMessage(Base, TimestampMixin):
    """Messages within support tickets"""
    __tablename__ = "support_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to user
    
    attachments = Column(JSON, default=list)  # [{filename, url, size}]
    
    ticket = relationship("SupportTicket", back_populates="messages")
    sender = relationship("User")


# =============================================================================
# CUSTOMER QUERIES (Public Contact Form)
# =============================================================================

class CustomerQuery(Base, TimestampMixin):
    """Customer queries from public contact form (no authentication required)"""
    __tablename__ = "customer_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact Info
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Query Details
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="general")  # general, sales, support, partnership, other
    
    # Status & Tracking
    status = Column(Enum(QueryStatus), default=QueryStatus.NEW, nullable=False, index=True)
    admin_notes = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    responded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Metadata
    source = Column(String(50), default="website")  # website, api, chatbot
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Relationships
    responded_by = relationship("User", foreign_keys=[responded_by_id])
    
    __table_args__ = (
        Index("idx_queries_status_created", "status", "created_at"),
        Index("idx_queries_email", "email"),
    )


# =============================================================================
# ENTERPRISE CONTACT REQUESTS (Talk to Us)
# =============================================================================

class EnterpriseContactStatus(str, PyEnum):
    """Status for enterprise contact requests"""
    PENDING = "pending"
    CONTACTED = "contacted"
    IN_PROGRESS = "in_progress"
    QUALIFIED = "qualified"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class EnterpriseContactRequest(Base, TimestampMixin):
    """
    Enterprise plan contact requests ("Talk to Us" form).
    Tracked separately for sales pipeline management.
    """
    __tablename__ = "enterprise_contact_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact Information
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    job_title = Column(String(100), nullable=True)
    
    # Company Information
    company_name = Column(String(200), nullable=False)
    company_size = Column(String(50), nullable=True)  # "1-10", "11-50", "51-200", "201-500", "500+"
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Requirements
    estimated_monthly_rows = Column(String(50), nullable=True)  # "1M-10M", "10M-100M", "100M+"
    use_case = Column(Text, nullable=True)  # Description of their data generation needs
    required_features = Column(JSON, default=list)  # List of specific features needed
    current_solution = Column(String(255), nullable=True)  # What they currently use
    timeline = Column(String(50), nullable=True)  # "immediately", "1-3 months", "3-6 months", "exploring"
    budget_range = Column(String(50), nullable=True)  # "under_500", "500_2000", "2000_5000", "5000_plus"
    
    # Additional Context
    message = Column(Text, nullable=True)
    how_heard_about_us = Column(String(100), nullable=True)  # "google", "linkedin", "referral", etc.
    
    # Sales Pipeline
    status = Column(Enum(EnterpriseContactStatus), default=EnterpriseContactStatus.PENDING, nullable=False, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Admin Notes & Follow-up
    admin_notes = Column(Text, nullable=True)
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    next_follow_up_at = Column(DateTime(timezone=True), nullable=True)
    
    # Outcome
    deal_value = Column(Integer, nullable=True)  # Potential/actual deal value in cents
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_reason = Column(Text, nullable=True)
    
    # If they become a customer
    converted_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    source = Column(String(50), default="pricing_page")  # "pricing_page", "contact_form", "landing_page"
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    converted_user = relationship("User", foreign_keys=[converted_user_id])
    
    __table_args__ = (
        Index("idx_enterprise_requests_status", "status"),
        Index("idx_enterprise_requests_assigned", "assigned_to_id"),
        Index("idx_enterprise_requests_created", "created_at"),
        Index("idx_enterprise_requests_company", "company_name"),
    )
