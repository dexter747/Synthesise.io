"""
Subscription and billing endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
)
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import (
    PlanResponse,
    SubscriptionResponse,
    SubscriptionDetailResponse,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    BillingPortalResponse,
    InvoiceResponse,
    PaymentMethodResponse,
    UsageResponse,
    CouponValidation,
    CouponResponse,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# PLANS
# =============================================================================

@router.get(
    "/plans",
    response_model=List[PlanResponse],
    summary="List available plans",
)
def list_plans(
    db: DBSession,
    active_only: bool = Query(True, description="Only return active plans"),
):
    """List all available subscription plans."""
    subscription_service = SubscriptionService(db)
    plans = subscription_service.get_plans(active_only=active_only)
    
    return [
        PlanResponse(
            id=p.id,
            name=p.name,
            slug=p.tier.value.lower(),
            description=p.description,
            tier=p.tier,
            price_monthly=float(p.monthly_price_cents / 100) if p.monthly_price_cents else 0.0,
            price_yearly=float(p.annual_price_cents / 100) if p.annual_price_cents else 0.0,
            features=p.features or {},
            limits={
                "monthly_data_gb": p.monthly_data_limit_gb,
                "max_datasets": p.max_datasets,
                "max_api_keys": p.max_api_keys,
                "max_team_members": p.max_team_members,
                "api_rate_limit_per_minute": p.api_rate_limit_per_minute,
                "retention_days": p.retention_days,
            },
            is_active=p.is_active,
            is_recommended=False,
        )
        for p in plans
    ]


@router.get(
    "/plans/{plan_id}",
    response_model=PlanResponse,
    summary="Get plan details",
)
def get_plan(
    plan_id: UUID,
    db: DBSession,
):
    """Get detailed information about a specific plan."""
    subscription_service = SubscriptionService(db)
    plan = subscription_service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    
    return PlanResponse(
        id=plan.id,
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        tier=plan.tier,
        price_monthly=float(plan.price_monthly) if plan.price_monthly else 0.0,
        price_yearly=float(plan.price_yearly) if plan.price_yearly else 0.0,
        features=plan.features or {},
        limits=plan.limits or {},
        is_active=plan.is_active,
        is_recommended=plan.is_recommended or False,
    )


# =============================================================================
# CURRENT SUBSCRIPTION
# =============================================================================

@router.get(
    "/current",
    response_model=SubscriptionDetailResponse,
    summary="Get current subscription",
)
@router.get(
    "/me",
    response_model=SubscriptionDetailResponse,
    summary="Get current subscription",
    include_in_schema=False,  # Alias for /current
)
def get_current_subscription(
    db: DBSession,
    user: CurrentUser,
):
    """Get current user's active subscription."""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    return SubscriptionDetailResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        plan_name=subscription.plan.name if subscription.plan else None,
        status=subscription.status,
        billing_cycle=subscription.billing_cycle,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end or False,
        cancelled_at=subscription.cancelled_at,
        trial_start=subscription.trial_start,
        trial_end=subscription.trial_end,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
        features=subscription.plan.features if subscription.plan else {},
        limits=subscription.plan.limits if subscription.plan else {},
    )


@router.get(
    "/usage",
    response_model=UsageResponse,
    summary="Get subscription usage",
)
def get_subscription_usage(
    db: DBSession,
    user: CurrentUser,
):
    """Get current period usage statistics."""
    subscription_service = SubscriptionService(db)
    usage = subscription_service.get_usage(user.id)
    
    return UsageResponse(
        period_start=usage.get("period_start"),
        period_end=usage.get("period_end"),
        api_calls_used=usage.get("api_calls_used", 0),
        api_calls_limit=usage.get("api_calls_limit", 0),
        rows_generated=usage.get("rows_generated", 0),
        rows_limit=usage.get("rows_limit", 0),
        datasets_count=usage.get("datasets_count", 0),
        datasets_limit=usage.get("datasets_limit", 0),
        storage_used_mb=usage.get("storage_used_mb", 0.0),
        storage_limit_mb=usage.get("storage_limit_mb", 0.0),
    )


# =============================================================================
# CHECKOUT & BILLING
# =============================================================================

@router.post(
    "/checkout",
    response_model=CheckoutSessionResponse,
    summary="Create checkout session",
)
def create_checkout_session(
    data: CheckoutSessionCreate,
    db: DBSession,
    user: CurrentUser,
    request: Request,
):
    """Create a Stripe checkout session for subscription."""
    subscription_service = SubscriptionService(db)
    
    # Get base URL for redirects
    base_url = str(request.base_url).rstrip("/")
    success_url = data.success_url or f"{base_url}/billing/success"
    cancel_url = data.cancel_url or f"{base_url}/billing/cancel"
    
    session = subscription_service.create_checkout_session(
        user_id=user.id,
        plan_id=data.plan_id,
        billing_cycle=data.billing_cycle,
        coupon_code=data.coupon_code,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return CheckoutSessionResponse(
        session_id=session.get("session_id") or session.get("checkout_id"),
        checkout_url=session["checkout_url"],
    )


@router.post(
    "/portal",
    response_model=BillingPortalResponse,
    summary="Create billing portal session",
)
def create_billing_portal(
    db: DBSession,
    user: CurrentUser,
    request: Request,
    return_url: Optional[str] = Query(None, description="Return URL after portal"),
):
    """Create a Stripe billing portal session for subscription management."""
    subscription_service = SubscriptionService(db)
    
    base_url = str(request.base_url).rstrip("/")
    return_url = return_url or f"{base_url}/billing"
    
    portal = subscription_service.create_billing_portal(
        user_id=user.id,
        return_url=return_url,
    )
    
    return BillingPortalResponse(
        portal_url=portal["portal_url"],
    )


@router.post(
    "/cancel",
    response_model=MessageResponse,
    summary="Cancel subscription",
)
def cancel_subscription(
    db: DBSession,
    user: CurrentUser,
    immediate: bool = Query(False, description="Cancel immediately vs at period end"),
):
    """Cancel current subscription."""
    subscription_service = SubscriptionService(db)
    subscription_service.cancel(user.id, immediate=immediate)
    
    if immediate:
        return MessageResponse(message="Subscription cancelled immediately")
    return MessageResponse(message="Subscription will be cancelled at end of billing period")


@router.post(
    "/resume",
    response_model=MessageResponse,
    summary="Resume cancelled subscription",
)
def resume_subscription(
    db: DBSession,
    user: CurrentUser,
):
    """Resume a subscription that was set to cancel at period end."""
    subscription_service = SubscriptionService(db)
    subscription_service.resume(user.id)
    return MessageResponse(message="Subscription resumed successfully")


# =============================================================================
# INVOICES
# =============================================================================

@router.get(
    "/invoices",
    response_model=List[InvoiceResponse],
    summary="List invoices",
)
def list_invoices(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """List user's invoices."""
    subscription_service = SubscriptionService(db)
    invoices, total = subscription_service.get_invoices(
        user_id=user.id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return [
        InvoiceResponse(
            id=i.id,
            invoice_number=i.invoice_number,
            amount=float(i.amount) if i.amount else 0.0,
            currency=i.currency or "USD",
            status=i.status,
            invoice_date=i.invoice_date,
            due_date=i.due_date,
            paid_date=i.paid_date,
            invoice_url=i.invoice_url,
            pdf_url=i.pdf_url,
        )
        for i in invoices
    ]


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get invoice details",
)
def get_invoice(
    invoice_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get detailed invoice information."""
    subscription_service = SubscriptionService(db)
    invoice = subscription_service.get_invoice(invoice_id, user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        amount=float(invoice.amount) if invoice.amount else 0.0,
        currency=invoice.currency or "USD",
        status=invoice.status,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        invoice_url=invoice.invoice_url,
        pdf_url=invoice.pdf_url,
    )


@router.get(
    "/invoices/{invoice_id}/download",
    summary="Download invoice PDF",
)
def download_invoice(
    invoice_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get invoice PDF download URL."""
    subscription_service = SubscriptionService(db)
    invoice = subscription_service.get_invoice(invoice_id, user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    
    if not invoice.pdf_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not available for this invoice",
        )
    
    return RedirectResponse(url=invoice.pdf_url)


# =============================================================================
# PAYMENT METHODS
# =============================================================================

@router.get(
    "/payment-methods",
    response_model=List[PaymentMethodResponse],
    summary="List payment methods",
)
def list_payment_methods(
    db: DBSession,
    user: CurrentUser,
):
    """List user's payment methods."""
    subscription_service = SubscriptionService(db)
    methods = subscription_service.get_payment_methods(user.id)
    
    return [
        PaymentMethodResponse(
            id=m.get("id"),
            type=m.get("type"),
            brand=m.get("brand"),
            last_four=m.get("last_four"),
            exp_month=m.get("exp_month"),
            exp_year=m.get("exp_year"),
            is_default=m.get("is_default", False),
        )
        for m in methods
    ]


@router.post(
    "/payment-methods/{method_id}/default",
    response_model=MessageResponse,
    summary="Set default payment method",
)
def set_default_payment_method(
    method_id: str,
    db: DBSession,
    user: CurrentUser,
):
    """Set a payment method as default."""
    subscription_service = SubscriptionService(db)
    subscription_service.set_default_payment_method(user.id, method_id)
    return MessageResponse(message="Default payment method updated")


@router.delete(
    "/payment-methods/{method_id}",
    response_model=MessageResponse,
    summary="Delete payment method",
)
def delete_payment_method(
    method_id: str,
    db: DBSession,
    user: CurrentUser,
):
    """Delete a payment method."""
    subscription_service = SubscriptionService(db)
    subscription_service.delete_payment_method(user.id, method_id)
    return MessageResponse(message="Payment method deleted")


# =============================================================================
# COUPONS
# =============================================================================

@router.post(
    "/coupons/validate",
    response_model=CouponResponse,
    summary="Validate coupon code",
)
def validate_coupon(
    data: CouponValidation,
    db: DBSession,
    user: CurrentUser,
):
    """Validate a coupon code and return discount information."""
    subscription_service = SubscriptionService(db)
    result = subscription_service.validate_coupon(data.code, data.plan_id)
    
    if not result or not result.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message if result else "Invalid or expired coupon code",
        )
    
    return CouponResponse(
        code=result.code,
        discount_type=result.discount_type,
        discount_value=result.discount_value,
        description=result.description,
        valid_until=None,  # Not exposed in response
    )


# =============================================================================
# STRIPE WEBHOOKS
# =============================================================================

@router.post(
    "/webhooks/stripe",
    include_in_schema=False,
)
def stripe_webhook(
    request: Request,
    db: DBSession,
):
    """
    Handle Stripe webhook events.
    This endpoint is called by Stripe to notify us of subscription events.
    """
    import stripe
    from app.core.config import settings
    
    payload = request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    subscription_service = SubscriptionService(db)
    
    # Handle different event types
    event_type = event["type"]
    data = event["data"]["object"]
    
    if event_type == "checkout.session.completed":
        subscription_service.handle_checkout_completed(data)
    elif event_type == "invoice.paid":
        subscription_service.handle_invoice_paid(data)
    elif event_type == "invoice.payment_failed":
        subscription_service.handle_payment_failed(data)
    elif event_type == "customer.subscription.updated":
        subscription_service.handle_subscription_updated(data)
    elif event_type == "customer.subscription.deleted":
        subscription_service.handle_subscription_deleted(data)
    
    return {"status": "success"}
