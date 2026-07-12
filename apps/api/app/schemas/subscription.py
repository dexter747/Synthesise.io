"""
Subscription and billing schemas for Synthesize.io API.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# SUBSCRIPTION PLAN SCHEMAS
# =============================================================================

class PlanFeatures(BaseSchema):
    """Subscription plan features."""
    
    max_rows_per_month: int
    max_datasets: int
    max_rows_per_request: int
    max_api_keys: int
    max_team_members: int
    max_organizations: int
    data_retention_days: int
    support_level: str
    custom_templates: bool
    api_access: bool
    priority_processing: bool
    dedicated_support: bool
    sla_guarantee: bool
    custom_models: bool
    on_premise: bool


class SubscriptionPlanResponse(BaseSchema):
    """Subscription plan details."""
    
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    monthly_price_cents: Optional[int] = None
    annual_price_cents: Optional[int] = None
    currency: str = "USD"
    features: Optional[PlanFeatures] = None
    limits: Optional[dict] = None
    is_popular: bool = False
    is_recommended: bool = False
    is_enterprise: bool = False
    sort_order: int = 0
    is_active: bool = True


class SubscriptionPlanListResponse(BaseSchema):
    """List of available plans."""
    
    plans: list[SubscriptionPlanResponse]


# =============================================================================
# SUBSCRIPTION SCHEMAS
# =============================================================================

class SubscriptionCreate(BaseSchema):
    """Create subscription (internal use)."""
    
    plan_id: UUID
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")
    payment_method: str = Field("dodo", pattern="^(dodo|razorpay)$")


class SubscriptionUpdate(BaseSchema):
    """Update subscription."""
    
    plan_id: Optional[UUID] = None
    billing_cycle: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    auto_renew: Optional[bool] = None


class SubscriptionResponse(BaseSchema, TimestampMixin):
    """Subscription details."""
    
    id: UUID
    user_id: UUID
    organization_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    plan_name: Optional[str] = None
    status: str
    billing_cycle: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Current usage
    rows_used: int = 0
    rows_limit: int = 0
    api_calls_used: int = 0
    api_calls_limit: int = 0


class SubscriptionDetailResponse(SubscriptionResponse):
    """Detailed subscription info."""
    
    plan: Optional[SubscriptionPlanResponse] = None
    payment_method: Optional[dict] = None
    next_billing_date: Optional[datetime] = None
    next_billing_amount: Optional[Decimal] = None


# =============================================================================
# CHECKOUT SCHEMAS
# =============================================================================

class CheckoutRequest(BaseSchema):
    """Initiate checkout for subscription."""
    
    plan_id: UUID
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")
    payment_method: str = Field("dodo", pattern="^(dodo|razorpay)$")
    coupon_code: Optional[str] = None
    organization_id: Optional[UUID] = None


class CheckoutResponse(BaseSchema):
    """Checkout initiation response."""
    
    checkout_id: str
    approval_url: str  # URL to redirect user for payment
    amount: Decimal
    currency: str
    expires_at: datetime


class CheckoutCompleteRequest(BaseSchema):
    """Complete checkout after payment approval."""
    
    checkout_id: str
    payment_id: str  # From payment provider


# =============================================================================
# PAYMENT SCHEMAS
# =============================================================================

class PaymentResponse(BaseSchema, TimestampMixin):
    """Payment record."""
    
    id: UUID
    subscription_id: Optional[UUID]
    user_id: UUID
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    provider_payment_id: Optional[str]
    description: Optional[str]
    paid_at: Optional[datetime]


class PaymentListResponse(PaginatedResponse[PaymentResponse]):
    """Paginated list of payments."""
    pass


# =============================================================================
# INVOICE SCHEMAS
# =============================================================================

class InvoiceLineItem(BaseSchema):
    """Invoice line item."""
    
    description: str
    quantity: int
    unit_price: Decimal
    amount: Decimal


class InvoiceResponse(BaseSchema, TimestampMixin):
    """Invoice details."""
    
    id: UUID
    invoice_number: str
    subscription_id: Optional[UUID]
    user_id: UUID
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    currency: str
    due_date: datetime
    paid_at: Optional[datetime]
    line_items: list[InvoiceLineItem] = []
    pdf_url: Optional[str] = None


class InvoiceListResponse(PaginatedResponse[InvoiceResponse]):
    """Paginated list of invoices."""
    pass


# =============================================================================
# COUPON SCHEMAS
# =============================================================================

class CouponValidateRequest(BaseSchema):
    """Validate coupon code."""
    
    code: str
    plan_id: Optional[UUID] = None
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")


class CouponValidateResponse(BaseSchema):
    """Coupon validation result."""
    
    valid: bool
    code: str
    discount_type: Optional[str] = None  # "percentage" or "fixed"
    discount_value: Optional[Decimal] = None
    description: Optional[str] = None
    original_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    error_message: Optional[str] = None


# =============================================================================
# BILLING SCHEMAS
# =============================================================================

class BillingInfoUpdate(BaseSchema):
    """Update billing information."""
    
    company_name: Optional[str] = Field(None, max_length=200)
    tax_id: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)  # ISO 3166-1 alpha-2


class BillingInfoResponse(BaseSchema):
    """Billing information."""
    
    company_name: Optional[str]
    tax_id: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]


class BillingPortalResponse(BaseSchema):
    """Billing portal access."""
    
    portal_url: str
    expires_at: Optional[datetime] = None


# =============================================================================
# USAGE SCHEMAS
# =============================================================================

class UsageSummaryResponse(BaseSchema):
    """Current usage summary."""
    
    period_start: datetime
    period_end: datetime
    
    # Row usage
    rows_used: int
    rows_limit: int
    rows_percentage: float
    
    # API calls
    api_calls_used: int
    api_calls_limit: int
    api_calls_percentage: float
    
    # Storage
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_percentage: float
    
    # Datasets
    datasets_count: int
    datasets_limit: int


class UsageHistoryItem(BaseSchema):
    """Historical usage item."""
    
    date: datetime
    rows_generated: int
    api_calls: int
    storage_delta_bytes: int


class UsageHistoryResponse(BaseSchema):
    """Usage history."""
    
    items: list[UsageHistoryItem]
    total_rows: int
    total_api_calls: int


# =============================================================================
# ADDITIONAL ENDPOINT SCHEMAS
# =============================================================================

class PlanResponse(BaseSchema):
    """Subscription plan response for endpoints."""
    
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    tier: Optional[str] = None
    price_monthly: Optional[float] = 0.0
    price_yearly: Optional[float] = 0.0
    features: dict = {}
    limits: dict = {}
    is_active: bool = True
    is_recommended: bool = False


class CheckoutSessionCreate(BaseSchema):
    """Create checkout session request."""
    
    plan_id: UUID
    billing_cycle: str = Field("monthly", pattern="^(monthly|yearly)$")
    coupon_code: Optional[str] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutSessionResponse(BaseSchema):
    """Checkout session response."""
    
    session_id: str
    checkout_url: str


class PaymentMethodResponse(BaseSchema):
    """Payment method info."""
    
    id: str
    type: str
    brand: Optional[str] = None
    last_four: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False


class UsageResponse(BaseSchema):
    """Current period usage."""
    
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    api_calls_used: int = 0
    api_calls_limit: int = 0
    rows_generated: int = 0
    rows_limit: int = 0
    datasets_count: int = 0
    datasets_limit: int = 0
    storage_used_mb: float = 0.0
    storage_limit_mb: float = 0.0


class CouponValidation(BaseSchema):
    """Coupon validation request."""
    
    code: str
    plan_id: Optional[UUID] = None


class CouponResponse(BaseSchema):
    """Coupon validation response."""
    
    code: str
    discount_type: str  # percentage, fixed
    discount_value: float
    description: Optional[str] = None
    valid_until: Optional[datetime] = None
