"""
Payment integrations for Synthesize.io
=====================================
Uses Dodo Payments as the sole payment provider.

Features:
- Subscription checkout sessions
- Webhook handling for payment events
- Automatic invoice generation
- Failed payment retry logic
- Subscription renewal automation
- Grace period management

NOTE: Refunds are NOT supported - all sales are final.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import json
import logging
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field

from app.api.deps import get_db, CurrentUser, DBSession, OptionalUser
from app.models import (
    User, Organization, Subscription, SubscriptionPlan, Payment, Invoice,
    SubscriptionStatus, PaymentStatus, PaymentProvider, BillingCycle,
    SubscriptionTier, EnterpriseContactRequest, EnterpriseContactStatus
)
from app.services.dodo_payments_service import (
    get_dodo_payments_service, 
    DodoPaymentsService,
    DodoPaymentsError,
    DodoProductId,
    DodoWebhookEvent,
)
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
GRACE_PERIOD_DAYS = 7
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAYS = [1, 3, 7]  # Days between retries


# ============================================================================
# SCHEMAS
# ============================================================================

class CreateCheckoutRequest(BaseModel):
    """Request to create a Dodo checkout session"""
    tier: str = Field(..., description="Subscription tier: 'pro' or 'business'")
    billing_cycle: str = Field("monthly", description="'monthly' or 'annual'")
    return_url: str = Field(..., description="URL to redirect after successful payment")
    
class CheckoutResponse(BaseModel):
    """Response with checkout URL"""
    checkout_url: str
    session_id: Optional[str] = None
    tier: str
    billing_cycle: str

class EnterpriseContactCreateRequest(BaseModel):
    """Enterprise contact request (Talk to Us)"""
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    company_size: Optional[str] = None
    use_case: Optional[str] = None
    estimated_rows_per_month: Optional[int] = None
    message: Optional[str] = None

class EnterpriseContactResponse(BaseModel):
    """Enterprise contact response"""
    id: UUID
    status: str
    message: str
    created_at: datetime

class PaymentHistoryResponse(BaseModel):
    """Payment history item"""
    id: UUID
    amount_cents: int
    currency: str
    status: str
    created_at: datetime
    description: Optional[str] = None

class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: UUID
    number: str
    amount_cents: int
    currency: str
    status: str
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None
    created_at: datetime


# ============================================================================
# CHECKOUT ENDPOINTS
# ============================================================================

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Create a Dodo Payments checkout session for Beginner, Pro, or Business subscription.
    
    - Beginner: $19/month or $190/year
    - Pro: $49/month or $470/year
    - Business: $299/month or $2,870/year
    - Enterprise: Use /enterprise/contact endpoint
    """
    tier = request.tier.lower()
    
    # Validate tier
    if tier not in ["beginner", "pro", "business"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid tier. Use 'beginner', 'pro', or 'business'. For enterprise, use /enterprise/contact"
        )
    
    # Get the product ID
    if tier == "beginner":
        product_id = DodoProductId.BEGINNER.value
    elif tier == "pro":
        product_id = DodoProductId.PRO.value
    else:
        product_id = DodoProductId.BUSINESS.value
    
    # Get user's name - construct from first_name/last_name or use email
    customer_name = None
    if current_user.first_name or current_user.last_name:
        customer_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
    if not customer_name:
        customer_name = current_user.email.split("@")[0]
    
    # Get the Dodo service
    dodo = get_dodo_payments_service()
    
    # Check if API key is configured
    if not dodo.api_key:
        raise HTTPException(
            status_code=503,
            detail="Payment service is not configured. Please contact support or set DODO_PAYMENTS_API_KEY environment variable."
        )
    
    try:
        # Create checkout session
        logger.info(f"Creating checkout for user {current_user.email}, tier: {tier}, product_id: {product_id}")
        session = await dodo.create_checkout_session(
            product_id=product_id,
            customer_email=current_user.email,
            customer_name=customer_name,
            return_url=request.return_url,
            metadata={
                "user_id": str(current_user.id),
                "tier": tier,
                "billing_cycle": request.billing_cycle,
            },
        )
        
        return CheckoutResponse(
            checkout_url=session.get("checkout_url", ""),
            session_id=session.get("session_id"),
            tier=tier,
            billing_cycle=request.billing_cycle,
        )
    except DodoPaymentsError as e:
        logger.error(f"Dodo checkout error: {e.message}, status: {e.status_code}, details: {e.details}")
        # Return detailed error for debugging
        detail = f"Payment service error: {e.message}"
        if e.details:
            detail += f" - {e.details}"
        raise HTTPException(status_code=500, detail=detail)


@router.post("/test/activate-subscription")
async def test_activate_subscription(
    request: CreateCheckoutRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    TEST ONLY: Manually activate a subscription without payment.
    Use this to test the subscription system in development.
    
    This simulates what the webhook does when payment succeeds.
    """
    tier_str = request.tier.lower()
    
    if tier_str not in ["beginner", "pro", "business"]:
        raise HTTPException(status_code=400, detail="Invalid tier. Use 'beginner', 'pro', or 'business'")
    
    # Map tier string to enum
    tier_map = {
        "beginner": SubscriptionTier.BEGINNER,
        "pro": SubscriptionTier.PRO,
        "business": SubscriptionTier.BUSINESS,
    }
    tier = tier_map[tier_str]
    
    # Get the plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.tier == tier
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Cancel any existing active subscriptions
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
    ).all()
    
    for sub in existing:
        sub.status = SubscriptionStatus.CANCELLED
        sub.cancelled_at = datetime.utcnow()
    
    # Create new subscription
    import uuid
    now = datetime.utcnow()
    period_end = now + timedelta(days=30)
    
    # Map tier to product ID
    product_id_map = {
        "beginner": DodoProductId.BEGINNER.value,
        "pro": DodoProductId.PRO.value,
        "business": DodoProductId.BUSINESS.value,
    }
    
    new_sub = Subscription(
        id=uuid.uuid4(),
        user_id=current_user.id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
        current_period_start=now,
        current_period_end=period_end,
        dodo_subscription_id=f"test_sub_{uuid.uuid4().hex[:12]}",
        dodo_customer_id=f"test_cust_{uuid.uuid4().hex[:12]}",
        dodo_product_id=product_id_map[tier_str],
        payment_provider=PaymentProvider.DODO,
    )
    
    db.add(new_sub)
    
    # Update organization tier
    if current_user.primary_organization_id:
        org = db.query(Organization).filter(
            Organization.id == current_user.primary_organization_id
        ).first()
        
        if org:
            org.subscription_tier = tier
            logger.info(f"Updated organization {org.id} tier to {tier.value}")
    
    db.commit()
    
    return {
        "message": "Subscription activated (TEST MODE)",
        "subscription_id": str(new_sub.id),
        "tier": tier.value,
        "status": "active",
        "period_end": period_end.isoformat()
    }


@router.get("/checkout/url")
async def get_checkout_url(
    tier: str,
    return_url: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a static checkout URL (no API call needed).
    Useful for embedding in emails or direct links.
    """
    tier = tier.lower()
    
    if tier not in ["beginner", "pro", "business"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid tier. Use 'beginner', 'pro', or 'business'."
        )
    
    if tier == "beginner":
        product_id = DodoProductId.BEGINNER.value
    elif tier == "pro":
        product_id = DodoProductId.PRO.value
    else:
        product_id = DodoProductId.BUSINESS.value
    customer_name = current_user.full_name or current_user.email.split("@")[0]
    
    dodo = get_dodo_payments_service()
    url = dodo.get_static_checkout_url(
        product_id=product_id,
        return_url=return_url,
        customer_email=current_user.email,
        customer_name=customer_name,
        metadata={"user_id": str(current_user.id)},
    )
    
    return {"checkout_url": url, "tier": tier}


# ============================================================================
# ENTERPRISE CONTACT ENDPOINTS
# ============================================================================

@router.post("/enterprise/contact", response_model=EnterpriseContactResponse)
async def enterprise_contact(
    request: EnterpriseContactCreateRequest,
    db: DBSession,
    current_user: OptionalUser = None,
):
    """
    Submit an enterprise contact request (Talk to Us).
    Available for both authenticated and unauthenticated users.
    """
    import uuid
    
    # Create enterprise contact request
    contact = EnterpriseContactRequest(
        id=uuid.uuid4(),
        user_id=current_user.id if current_user else None,
        company_name=request.company_name,
        contact_name=request.contact_name,
        email=request.email,
        phone=request.phone,
        company_size=request.company_size,
        use_case=request.use_case,
        estimated_rows_per_month=request.estimated_rows_per_month,
        requirements={"message": request.message} if request.message else {},
        status=EnterpriseContactStatus.PENDING,
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    # TODO: Send notification email to sales team
    logger.info(f"New enterprise contact request: {contact.id} from {request.email}")
    
    return EnterpriseContactResponse(
        id=contact.id,
        status=contact.status.value,
        message="Thank you for your interest! Our team will contact you within 24 hours.",
        created_at=contact.created_at,
    )


# ============================================================================
# DODO WEBHOOKS
# ============================================================================

@router.post("/webhooks/dodo")
async def handle_dodo_webhook(
    request: Request,
    db: DBSession,
    background_tasks: BackgroundTasks,
    webhook_id: str = Header(None, alias="webhook-id"),
    webhook_signature: str = Header(None, alias="webhook-signature"),
    webhook_timestamp: str = Header(None, alias="webhook-timestamp"),
):
    """
    Handle Dodo Payments webhook events.
    
    Configure webhook URL in Dodo dashboard:
    https://your-domain.com/api/v1/payments/webhooks/dodo
    
    Events handled:
    - subscription.active: New subscription activated
    - subscription.on_hold: Payment failed, subscription paused
    - subscription.renewed: Subscription successfully renewed
    - subscription.cancelled: Subscription cancelled
    - payment.succeeded: Payment completed
    - payment.failed: Payment failed
    """
    # Get raw body for signature verification
    body = await request.body()
    
    dodo = get_dodo_payments_service()
    
    # Verify webhook signature
    if not dodo.verify_webhook_signature(
        payload=body,
        signature=webhook_signature or "",
        timestamp=webhook_timestamp or "",
        webhook_id=webhook_id or "",
    ):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Parse event
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event = dodo.parse_webhook_event(payload)
    event_type = event.get("type")
    event_data = event.get("data", {})
    
    logger.info(f"Received Dodo webhook: {event_type}")
    
    # Process event based on type
    if event_type == DodoWebhookEvent.SUBSCRIPTION_ACTIVE.value:
        background_tasks.add_task(
            process_subscription_active, db, event_data
        )
    
    elif event_type == DodoWebhookEvent.SUBSCRIPTION_ON_HOLD.value:
        background_tasks.add_task(
            process_subscription_on_hold, db, event_data
        )
    
    elif event_type == DodoWebhookEvent.SUBSCRIPTION_RENEWED.value:
        background_tasks.add_task(
            process_subscription_renewed, db, event_data
        )
    
    elif event_type == DodoWebhookEvent.SUBSCRIPTION_CANCELLED.value:
        background_tasks.add_task(
            process_subscription_cancelled, db, event_data
        )
    
    elif event_type == DodoWebhookEvent.PAYMENT_SUCCEEDED.value:
        background_tasks.add_task(
            process_payment_succeeded, db, event_data
        )
    
    elif event_type == DodoWebhookEvent.PAYMENT_FAILED.value:
        background_tasks.add_task(
            process_payment_failed, db, event_data
        )
    
    return {"status": "ok", "event": event_type}


# ============================================================================
# WEBHOOK EVENT HANDLERS
# ============================================================================

async def process_subscription_active(db: Session, event_data: dict):
    """Process subscription.active event - new subscription created"""
    try:
        subscription_id = event_data.get("subscription_id")
        customer_id = event_data.get("customer_id")
        product_id = event_data.get("product_id")
        metadata = event_data.get("metadata", {})
        
        user_id = metadata.get("user_id")
        if not user_id:
            logger.error(f"No user_id in subscription metadata: {subscription_id}")
            return
        
        # Determine tier from product_id
        if product_id == DodoProductId.PRO.value:
            tier = SubscriptionTier.PRO
        elif product_id == DodoProductId.BUSINESS.value:
            tier = SubscriptionTier.BUSINESS
        else:
            logger.error(f"Unknown product_id: {product_id}")
            return
        
        # Get or create subscription plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier
        ).first()
        
        if not plan:
            logger.error(f"Plan not found for tier: {tier}")
            return
        
        # Check for existing subscription
        existing = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).first()
        
        if existing:
            # Cancel old subscription
            existing.status = SubscriptionStatus.CANCELLED
            existing.cancelled_at = datetime.utcnow()
        
        # Create new subscription
        import uuid
        now = datetime.utcnow()
        period_end = now + timedelta(days=30)  # Dodo sends actual dates in webhook
        
        new_sub = Subscription(
            id=uuid.uuid4(),
            user_id=user_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=BillingCycle.MONTHLY,
            current_period_start=now,
            current_period_end=period_end,
            dodo_subscription_id=subscription_id,
            dodo_customer_id=customer_id,
            dodo_product_id=product_id,
            payment_provider=PaymentProvider.DODO,
        )
        
        db.add(new_sub)
        db.commit()
        
        # CRITICAL: Update user's organization tier for quota enforcement
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.primary_organization_id:
            org = db.query(Organization).filter(
                Organization.id == user.primary_organization_id
            ).first()
            
            if org:
                org.subscription_tier = tier
                db.commit()
                logger.info(f"Updated organization {org.id} tier to {tier.value}")
        
        logger.info(f"Created subscription for user {user_id}: {tier.value}")
        
    except Exception as e:
        logger.error(f"Error processing subscription.active: {e}")
        db.rollback()


async def process_subscription_on_hold(db: Session, event_data: dict):
    """Process subscription.on_hold event - payment failed"""
    try:
        subscription_id = event_data.get("subscription_id")
        
        subscription = db.query(Subscription).filter(
            Subscription.dodo_subscription_id == subscription_id
        ).first()
        
        if not subscription:
            logger.warning(f"Subscription not found: {subscription_id}")
            return
        
        subscription.status = SubscriptionStatus.ON_HOLD
        db.commit()
        
        logger.info(f"Subscription on hold: {subscription_id}")
        
        # TODO: Send email to user about failed payment
        
    except Exception as e:
        logger.error(f"Error processing subscription.on_hold: {e}")
        db.rollback()


async def process_subscription_renewed(db: Session, event_data: dict):
    """Process subscription.renewed event"""
    try:
        subscription_id = event_data.get("subscription_id")
        
        subscription = db.query(Subscription).filter(
            Subscription.dodo_subscription_id == subscription_id
        ).first()
        
        if not subscription:
            logger.warning(f"Subscription not found: {subscription_id}")
            return
        
        # Update period
        now = datetime.utcnow()
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.status = SubscriptionStatus.ACTIVE
        
        db.commit()
        
        logger.info(f"Subscription renewed: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error processing subscription.renewed: {e}")
        db.rollback()


async def process_subscription_cancelled(db: Session, event_data: dict):
    """Process subscription.cancelled event"""
    try:
        subscription_id = event_data.get("subscription_id")
        
        subscription = db.query(Subscription).filter(
            Subscription.dodo_subscription_id == subscription_id
        ).first()
        
        if not subscription:
            logger.warning(f"Subscription not found: {subscription_id}")
            return
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error processing subscription.cancelled: {e}")
        db.rollback()


async def process_payment_succeeded(db: Session, event_data: dict):
    """Process payment.succeeded event"""
    try:
        import uuid
        
        payment_id = event_data.get("payment_id")
        subscription_id = event_data.get("subscription_id")
        customer_id = event_data.get("customer_id")
        amount = event_data.get("amount", 0)
        currency = event_data.get("currency", "USD")
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.dodo_subscription_id == subscription_id
        ).first()
        
        # Create payment record
        payment = Payment(
            id=uuid.uuid4(),
            subscription_id=subscription.id if subscription else None,
            user_id=subscription.user_id if subscription else None,
            amount_cents=amount,
            currency=currency,
            status=PaymentStatus.COMPLETED,
            provider=PaymentProvider.DODO,
            dodo_payment_id=payment_id,
            dodo_customer_id=customer_id,
        )
        
        db.add(payment)
        
        # Create invoice
        invoice = Invoice(
            id=uuid.uuid4(),
            subscription_id=subscription.id if subscription else None,
            payment_id=payment.id,
            number=f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            amount_cents=amount,
            currency=currency,
            status="paid",
            paid_at=datetime.utcnow(),
        )
        
        db.add(invoice)
        db.commit()
        
        logger.info(f"Payment succeeded: {payment_id}")
        
    except Exception as e:
        logger.error(f"Error processing payment.succeeded: {e}")
        db.rollback()


async def process_payment_failed(db: Session, event_data: dict):
    """Process payment.failed event"""
    try:
        import uuid
        
        payment_id = event_data.get("payment_id")
        subscription_id = event_data.get("subscription_id")
        customer_id = event_data.get("customer_id")
        amount = event_data.get("amount", 0)
        currency = event_data.get("currency", "USD")
        error = event_data.get("error", {})
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.dodo_subscription_id == subscription_id
        ).first()
        
        # Create failed payment record
        payment = Payment(
            id=uuid.uuid4(),
            subscription_id=subscription.id if subscription else None,
            user_id=subscription.user_id if subscription else None,
            amount_cents=amount,
            currency=currency,
            status=PaymentStatus.FAILED,
            provider=PaymentProvider.DODO,
            dodo_payment_id=payment_id,
            dodo_customer_id=customer_id,
            failure_message=error.get("message"),
        )
        
        db.add(payment)
        db.commit()
        
        logger.info(f"Payment failed: {payment_id}")
        
        # TODO: Send email to user about failed payment
        
    except Exception as e:
        logger.error(f"Error processing payment.failed: {e}")
        db.rollback()


# ============================================================================
# SUBSCRIPTION MANAGEMENT
# ============================================================================

@router.post("/subscription/cancel")
async def cancel_subscription(
    db: DBSession,
    current_user: CurrentUser,
    cancel_immediately: bool = False,
):
    """
    Cancel current subscription.
    
    By default, cancels at period end (user keeps access until end of billing period).
    Set cancel_immediately=True to cancel right away.
    """
    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    if not subscription.dodo_subscription_id:
        raise HTTPException(status_code=400, detail="Cannot cancel manually created subscription")
    
    dodo = get_dodo_payments_service()
    
    try:
        await dodo.cancel_subscription(
            subscription_id=subscription.dodo_subscription_id,
            cancel_at_period_end=not cancel_immediately,
        )
        
        if cancel_immediately:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
        else:
            subscription.cancel_at_period_end = True
        
        db.commit()
        
        return {
            "status": "cancelled" if cancel_immediately else "scheduled_for_cancellation",
            "effective_date": subscription.current_period_end.isoformat() if not cancel_immediately else datetime.utcnow().isoformat(),
        }
    except DodoPaymentsError as e:
        logger.error(f"Cancel subscription error: {e.message}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.post("/subscription/change-plan")
async def change_plan(
    new_tier: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Upgrade or downgrade subscription plan.
    
    Changes are prorated immediately.
    """
    new_tier = new_tier.lower()
    
    if new_tier not in ["beginner", "pro", "business"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid tier. Use 'beginner', 'pro', or 'business'. For enterprise, use /enterprise/contact"
        )
    
    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    if not subscription.dodo_subscription_id:
        raise HTTPException(status_code=400, detail="Cannot change plan for manually created subscription")
    
    # Get new product ID
    if new_tier == "beginner":
        new_product_id = DodoProductId.BEGINNER.value
    elif new_tier == "pro":
        new_product_id = DodoProductId.PRO.value
    else:
        new_product_id = DodoProductId.BUSINESS.value
    
    # Check if already on this plan
    if subscription.dodo_product_id == new_product_id:
        raise HTTPException(status_code=400, detail="Already subscribed to this plan")
    
    dodo = get_dodo_payments_service()
    
    try:
        result = await dodo.change_subscription_plan(
            subscription_id=subscription.dodo_subscription_id,
            new_product_id=new_product_id,
        )
        
        # Update local subscription
        new_tier_enum = SubscriptionTier.PRO if new_tier == "pro" else SubscriptionTier.BUSINESS
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == new_tier_enum
        ).first()
        
        if plan:
            subscription.plan_id = plan.id
            subscription.dodo_product_id = new_product_id
            db.commit()
        
        return {
            "status": "success",
            "new_tier": new_tier,
            "effective_immediately": True,
        }
    except DodoPaymentsError as e:
        logger.error(f"Change plan error: {e.message}")
        raise HTTPException(status_code=500, detail="Failed to change plan")


@router.post("/subscription/update-payment-method")
async def update_payment_method(
    return_url: str,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a URL to update payment method for current subscription.
    This also reactivates subscriptions that are on_hold.
    """
    # Get subscription (including on_hold)
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.ON_HOLD])
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    if not subscription.dodo_subscription_id:
        raise HTTPException(status_code=400, detail="Cannot update payment for manually created subscription")
    
    dodo = get_dodo_payments_service()
    
    try:
        result = await dodo.update_payment_method(
            subscription_id=subscription.dodo_subscription_id,
            return_url=return_url,
        )
        
        return {
            "update_url": result.get("url", ""),
        }
    except DodoPaymentsError as e:
        logger.error(f"Update payment method error: {e.message}")
        raise HTTPException(status_code=500, detail="Failed to generate update URL")


# ============================================================================
# PAYMENT & INVOICE HISTORY
# ============================================================================

@router.get("/payments/history", response_model=List[PaymentHistoryResponse])
async def get_payment_history(
    db: DBSession,
    current_user: CurrentUser,
    limit: int = 20,
):
    """Get payment history for current user"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).limit(limit).all()
    
    return [
        PaymentHistoryResponse(
            id=p.id,
            amount_cents=p.amount_cents,
            currency=p.currency or "USD",
            status=p.status.value,
            created_at=p.created_at,
            description=f"Subscription payment",
        )
        for p in payments
    ]


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    db: DBSession,
    current_user: CurrentUser,
    limit: int = 20,
):
    """Get invoices for current user"""
    # Get user's subscriptions
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    if not subscriptions:
        return []
    
    sub_ids = [s.id for s in subscriptions]
    
    invoices = db.query(Invoice).filter(
        Invoice.subscription_id.in_(sub_ids)
    ).order_by(Invoice.created_at.desc()).limit(limit).all()
    
    return [
        InvoiceResponse(
            id=i.id,
            number=i.number,
            amount_cents=i.amount_cents,
            currency=i.currency or "USD",
            status=i.status,
            due_date=i.due_date,
            paid_at=i.paid_at,
            created_at=i.created_at,
        )
        for i in invoices
    ]


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific invoice"""
    # Get user's subscriptions
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    sub_ids = [s.id for s in subscriptions]
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.subscription_id.in_(sub_ids)
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return InvoiceResponse(
        id=invoice.id,
        number=invoice.number,
        amount_cents=invoice.amount_cents,
        currency=invoice.currency or "USD",
        status=invoice.status,
        due_date=invoice.due_date,
        paid_at=invoice.paid_at,
        created_at=invoice.created_at,
    )


# ============================================================================
# PRICING INFO
# ============================================================================

@router.get("/pricing")
async def get_pricing(db: DBSession):
    """Get current pricing information (USD only)"""
    plans = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True,
        SubscriptionPlan.is_public == True
    ).order_by(SubscriptionPlan.sort_order).all()
    
    return {
        "plans": [
            {
                "tier": p.tier.value,
                "name": p.name,
                "description": p.description,
                "monthly_price_usd": p.monthly_price_cents / 100 if p.monthly_price_cents > 0 else 0,
                "annual_price_usd": p.annual_price_cents / 100 if p.annual_price_cents > 0 else 0,
                "features": p.features,
                "limits": {
                    "monthly_data_limit_gb": p.monthly_data_limit_gb,
                    "max_datasets": p.max_datasets,
                    "max_api_keys": p.max_api_keys,
                    "max_team_members": p.max_team_members,
                    "api_rate_limit_per_minute": p.api_rate_limit_per_minute,
                    "retention_days": p.retention_days,
                },
                "is_enterprise": p.tier == SubscriptionTier.ENTERPRISE,
            }
            for p in plans
        ],
        "currency": "USD",
    }
