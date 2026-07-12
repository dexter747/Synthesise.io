"""
Subscription service for Synthesize.io API.

Handles subscription management, billing, and payment processing.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Session

from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PaymentError,
)
from app.models import (
    Subscription,
    SubscriptionPlan,
    Payment,
    Invoice,
    User,
    Coupon,
)
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionUpdate,
    CouponValidateRequest,
    CouponValidateResponse,
    BillingInfoUpdate,
)


class SubscriptionService:
    """Service for subscription and billing operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # PLANS
    # =========================================================================
    
    def get_plans(self, active_only: bool = True) -> list[SubscriptionPlan]:
        """Get all subscription plans."""
        query = select(SubscriptionPlan).order_by(SubscriptionPlan.sort_order)
        
        if active_only:
            query = query.where(SubscriptionPlan.is_active == True)
        
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def get_plan(self, plan_id: UUID) -> Optional[SubscriptionPlan]:
        """Get plan by ID."""
        result = self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    def get_plan_by_slug(self, slug: str) -> Optional[SubscriptionPlan]:
        """Get plan by slug."""
        result = self.db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.slug == slug)
        )
        return result.scalar_one_or_none()
    
    def get_plan_or_raise(self, plan_id: UUID) -> SubscriptionPlan:
        """Get plan by ID or raise NotFoundError."""
        plan = self.get_plan(plan_id)
        if not plan:
            raise NotFoundError("Plan", str(plan_id))
        return plan
    
    # =========================================================================
    # SUBSCRIPTIONS
    # =========================================================================
    
    def get_user_subscription(self, user_id: UUID) -> Optional[Subscription]:
        """Get user's active subscription."""
        result = self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.user_id == user_id)
            .where(Subscription.status.in_(["active", "trialing", "past_due"]))
            .order_by(Subscription.created_at.desc())
        )
        return result.scalars().first()
    
    def get_subscription(self, subscription_id: UUID) -> Optional[Subscription]:
        """Get subscription by ID."""
        result = self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()
    
    def get_subscription_or_raise(self, subscription_id: UUID) -> Subscription:
        """Get subscription or raise NotFoundError."""
        sub = self.get_subscription(subscription_id)
        if not sub:
            raise NotFoundError("Subscription", str(subscription_id))
        return sub
    
    def create_free_subscription(self, user_id: UUID) -> Subscription:
        """Create a free tier subscription for new user."""
        # Get free plan
        free_plan = self.get_plan_by_slug("free")
        if not free_plan:
            raise ValidationError("Free plan not found")
        
        # Check for existing subscription
        existing = self.get_user_subscription(user_id)
        if existing:
            return existing
        
        # Create subscription
        now = datetime.utcnow()
        subscription = Subscription(
            user_id=user_id,
            plan_id=free_plan.id,
            status="active",
            billing_cycle="monthly",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            cancel_at_period_end=False,
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def update_subscription(
        self, subscription_id: UUID, data: SubscriptionUpdate, user_id: UUID
    ) -> Subscription:
        """Update subscription settings."""
        sub = self.get_subscription_or_raise(subscription_id)
        
        # Verify ownership
        if sub.user_id != user_id:
            raise ValidationError("Not authorized to modify this subscription")
        
        # Update fields
        if data.auto_renew is not None:
            sub.cancel_at_period_end = not data.auto_renew
        
        self.db.commit()
        self.db.refresh(sub)
        
        return sub
    
    def cancel_subscription(
        self, subscription_id: UUID, user_id: UUID, immediately: bool = False
    ) -> Subscription:
        """Cancel subscription."""
        sub = self.get_subscription_or_raise(subscription_id)
        
        # Verify ownership
        if sub.user_id != user_id:
            raise ValidationError("Not authorized to cancel this subscription")
        
        if immediately:
            sub.status = "canceled"
            sub.canceled_at = datetime.utcnow()
        else:
            sub.cancel_at_period_end = True
            sub.canceled_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(sub)
        
        return sub
    
    # Alias for cancel_subscription - can accept user_id to find active subscription
    def cancel(self, user_id_or_sub_id: UUID, user_id: UUID = None, immediate: bool = False, immediately: bool = False) -> Subscription:
        """Cancel subscription by user_id or subscription_id."""
        # If user_id is None, assume first arg is user_id and find their active subscription
        if user_id is None:
            sub = self.get_user_subscription(user_id_or_sub_id)
            if not sub:
                raise NotFoundError("Subscription", str(user_id_or_sub_id))
            return self.cancel_subscription(sub.id, user_id_or_sub_id, immediate or immediately)
        else:
            # First arg is subscription_id, second is user_id
            return self.cancel_subscription(user_id_or_sub_id, user_id, immediate or immediately)
    
    def resume(self, subscription_id: UUID, user_id: UUID = None) -> Subscription:
        """Resume a canceled subscription (before period end)."""
        sub = self.get_subscription_or_raise(subscription_id)
        
        # Verify ownership if user_id provided
        if user_id and sub.user_id != user_id:
            raise ValidationError("Not authorized to resume this subscription")
        
        if sub.status == "canceled":
            raise ValidationError("Cannot resume a fully canceled subscription")
        
        sub.cancel_at_period_end = False
        sub.canceled_at = None
        
        self.db.commit()
        self.db.refresh(sub)
        
        return sub
    
    def get_usage(self, user_id: UUID) -> dict:
        """Get subscription usage for a user."""
        sub = self.get_user_subscription(user_id)
        if not sub or not sub.plan:
            return {
                "rows_generated": 0,
                "rows_limit": 0,
                "datasets_created": 0,
                "datasets_limit": 0,
                "percentage_used": 0,
            }
        
        # Get limits from plan
        limits = sub.plan.limits or {}
        
        return {
            "rows_generated": 0,  # TODO: Get from usage tracking
            "rows_limit": limits.get("rows_per_month", 0),
            "datasets_created": 0,  # TODO: Get from usage tracking
            "datasets_limit": limits.get("datasets", -1),
            "percentage_used": 0,
        }
    
    def create_checkout_session(
        self, 
        user_id: UUID, 
        plan_id: UUID, 
        billing_cycle: str = "monthly",
        success_url: str = None,
        cancel_url: str = None,
        coupon_code: str = None,
    ) -> dict:
        """Create a checkout session for subscription."""
        plan = self.get_plan_or_raise(plan_id)
        
        # For now, return a mock checkout session
        # TODO: Integrate with actual payment provider
        import uuid
        checkout_id = str(uuid.uuid4())
        
        return {
            "checkout_id": checkout_id,
            "checkout_url": f"/checkout/{checkout_id}",
            "plan_id": str(plan_id),
            "billing_cycle": billing_cycle,
            "amount": plan.monthly_price_cents if billing_cycle == "monthly" else plan.annual_price_cents,
            "currency": plan.currency or "USD",
        }
    
    def create_billing_portal(self, user_id: UUID, return_url: str = None) -> dict:
        """Create a billing portal session for managing subscription."""
        # TODO: Integrate with actual payment provider
        import uuid
        portal_id = str(uuid.uuid4())
        
        return {
            "portal_id": portal_id,
            "portal_url": f"/billing/{portal_id}",
            "return_url": return_url,
        }
    
    def get_payment_methods(self, user_id: UUID) -> list:
        """Get user's saved payment methods."""
        # TODO: Fetch from payment provider
        return []
    
    # =========================================================================
    # CHECKOUT
    # =========================================================================
    
    def initiate_checkout(
        self, data: CheckoutRequest, user_id: UUID
    ) -> CheckoutResponse:
        """Initiate checkout process for subscription."""
        # Get plan
        plan = self.get_plan_or_raise(data.plan_id)
        
        if not plan.is_active:
            raise ValidationError("This plan is not available")
        
        # Calculate price
        if data.billing_cycle == "yearly":
            base_price = plan.price_yearly
        else:
            base_price = plan.price_monthly
        
        # Apply coupon if provided
        discount = Decimal("0")
        if data.coupon_code:
            coupon_result = self.validate_coupon(
                CouponValidateRequest(
                    code=data.coupon_code,
                    plan_id=data.plan_id,
                    billing_cycle=data.billing_cycle,
                )
            )
            if coupon_result.valid:
                discount = coupon_result.discount_amount or Decimal("0")
        
        final_amount = max(base_price - discount, Decimal("0"))
        
        # Create payment based on provider
        if data.payment_method == "razorpay":
            checkout = self._create_razorpay_checkout(
                user_id=user_id,
                plan=plan,
                amount=final_amount,
                billing_cycle=data.billing_cycle,
                coupon_code=data.coupon_code,
            )
        elif data.payment_method == "dodo":
            # Dodo payments handled separately via /payments/checkout endpoint
            raise ValidationError("Please use /payments/checkout endpoint for Dodo payments")
        else:
            raise ValidationError(f"Unsupported payment method: {data.payment_method}")
        
        return checkout
    
    def complete_checkout(
        self,
        checkout_id: str,
        payment_id: str,
        payer_id: Optional[str] = None,
    ) -> Subscription:
        """Complete checkout after payment approval."""
        # TODO: Verify payment with provider
        # TODO: Create or update subscription
        # TODO: Create payment record
        # TODO: Generate invoice
        
        raise NotImplementedError("Checkout completion not yet implemented")
    
    # =========================================================================
    # COUPON VALIDATION
    # =========================================================================
    
    def validate_coupon(
        self, data_or_code, plan_id: UUID = None, billing_cycle: str = None
    ) -> CouponValidateResponse:
        """Validate a coupon code."""
        # Support both request object and individual args
        if isinstance(data_or_code, CouponValidateRequest):
            data = data_or_code
        else:
            # Create request from individual args
            data = CouponValidateRequest(
                code=str(data_or_code),
                plan_id=plan_id,
                billing_cycle=billing_cycle or "monthly",
            )
        
        # Get coupon
        result = self.db.execute(
            select(Coupon).where(
                and_(
                    Coupon.code == data.code.upper(),
                    Coupon.is_active == True,
                )
            )
        )
        coupon = result.scalar_one_or_none()
        
        if not coupon:
            return CouponValidateResponse(
                valid=False,
                code=data.code,
                error_message="Invalid coupon code",
            )
        
        # Check expiration
        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            return CouponValidateResponse(
                valid=False,
                code=data.code,
                error_message="Coupon has expired",
            )
        
        # Check usage limit
        if coupon.max_uses and coupon.times_used >= coupon.max_uses:
            return CouponValidateResponse(
                valid=False,
                code=data.code,
                error_message="Coupon usage limit reached",
            )
        
        # Check plan restrictions
        if coupon.applicable_plans:
            if str(data.plan_id) not in coupon.applicable_plans:
                return CouponValidateResponse(
                    valid=False,
                    code=data.code,
                    error_message="Coupon not valid for this plan",
                )
        
        # Calculate discount
        plan = self.get_plan_or_raise(data.plan_id)
        if data.billing_cycle == "yearly":
            original_amount = plan.price_yearly
        else:
            original_amount = plan.price_monthly
        
        if coupon.discount_type == "percentage":
            discount_amount = original_amount * (coupon.discount_value / 100)
        else:
            discount_amount = coupon.discount_value
        
        final_amount = max(original_amount - discount_amount, Decimal("0"))
        
        return CouponValidateResponse(
            valid=True,
            code=data.code,
            discount_type=coupon.discount_type,
            discount_value=coupon.discount_value,
            description=coupon.description,
            original_amount=original_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
        )
    
    # =========================================================================
    # INVOICES
    # =========================================================================
    
    def get_invoices(
        self, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[Invoice], int]:
        """Get user's invoices."""
        query = (
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.created_at.desc())
        )
        count_query = (
            select(func.count(Invoice.id))
            .where(Invoice.user_id == user_id)
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        invoices = list(result.scalars().all())
        
        return invoices, total
    
    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        result = self.db.execute(
            select(Invoice)
            .options(selectinload(Invoice.items))
            .where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()
    
    # =========================================================================
    # PAYMENTS
    # =========================================================================
    
    def get_payments(
        self, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[Payment], int]:
        """Get user's payment history."""
        query = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        count_query = (
            select(func.count(Payment.id))
            .where(Payment.user_id == user_id)
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        payments = list(result.scalars().all())
        
        return payments, total
    
    # =========================================================================
    # BILLING INFO
    # =========================================================================
    
    def update_billing_info(
        self, user_id: UUID, data: BillingInfoUpdate
    ) -> dict:
        """Update user's billing information."""
        result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(user_id))
        
        billing_info = user.billing_info or {}
        update_data = data.model_dump(exclude_unset=True)
        billing_info.update(update_data)
        
        user.billing_info = billing_info
        self.db.commit()
        
        return billing_info
    
    def get_billing_info(self, user_id: UUID) -> dict:
        """Get user's billing information."""
        result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(user_id))
        
        return user.billing_info or {}
    
    # =========================================================================
    # USAGE
    # =========================================================================
    
    def get_usage_summary(self, user_id: UUID) -> dict:
        """Get user's current usage summary."""
        from app.models import UsageRecord
        
        # Get subscription
        subscription = self.get_user_subscription(user_id)
        
        if subscription:
            period_start = subscription.current_period_start
            period_end = subscription.current_period_end
            features = subscription.plan.features or {}
            rows_limit = features.get("max_rows_per_month", 10000)
            api_limit = features.get("max_api_calls", 10000)
            storage_limit = features.get("max_storage_gb", 1) * 1024 * 1024 * 1024
        else:
            # Free tier defaults
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            rows_limit = 1000
            api_limit = 100
            storage_limit = 100 * 1024 * 1024  # 100 MB
        
        # Get usage records for period - convert datetime to date for comparison
        period_start_date = period_start.date() if hasattr(period_start, 'date') else period_start
        period_end_date = period_end.date() if hasattr(period_end, 'date') else period_end
        
        # Get datasets created in period (proxy for rows)
        rows_result = self.db.execute(
            select(func.sum(UsageRecord.datasets_created))
            .where(UsageRecord.user_id == user_id)
            .where(UsageRecord.date >= period_start_date)
            .where(UsageRecord.date <= period_end_date)
        )
        rows_used = rows_result.scalar() or 0
        
        # Get API calls in period
        api_result = self.db.execute(
            select(func.sum(UsageRecord.api_calls))
            .where(UsageRecord.user_id == user_id)
            .where(UsageRecord.date >= period_start_date)
            .where(UsageRecord.date <= period_end_date)
        )
        api_used = api_result.scalar() or 0
        
        # TODO: Calculate storage usage
        storage_used = 0
        
        return {
            "period_start": period_start,
            "period_end": period_end,
            "rows_used": rows_used,
            "rows_limit": rows_limit,
            "rows_percentage": (rows_used / rows_limit * 100) if rows_limit > 0 else 0,
            "api_calls_used": api_used,
            "api_calls_limit": api_limit,
            "api_calls_percentage": (api_used / api_limit * 100) if api_limit > 0 else 0,
            "storage_used_bytes": storage_used,
            "storage_limit_bytes": storage_limit,
            "storage_percentage": (storage_used / storage_limit * 100) if storage_limit > 0 else 0,
        }
    
    def get_platform_stats(self) -> dict:
        """Get platform-wide subscription statistics for admin dashboard."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        month_start = now - timedelta(days=30)
        
        # Total subscriptions
        total_result = self.db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.status.in_(["active", "trialing", "past_due"]))
        )
        total_subscriptions = total_result.scalar() or 0
        
        # Active subscribers
        active_result = self.db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.status == "active")
        )
        active_subscriptions = active_result.scalar() or 0
        
        # Trial subscriptions
        trial_result = self.db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.status == "trialing")
        )
        trial_subscriptions = trial_result.scalar() or 0
        
        # Monthly revenue (sum of active subscription prices)
        revenue_result = self.db.execute(
            select(func.sum(SubscriptionPlan.monthly_price_cents))
            .join(Subscription, Subscription.plan_id == SubscriptionPlan.id)
            .where(Subscription.status == "active")
            .where(Subscription.billing_cycle == "monthly")
        )
        monthly_revenue = float(revenue_result.scalar() or 0) / 100  # Convert cents to dollars
        
        # New subscriptions this month
        new_result = self.db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.created_at >= month_start)
        )
        new_this_month = new_result.scalar() or 0
        
        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "trial_subscriptions": trial_subscriptions,
            "monthly_revenue": monthly_revenue,
            "new_subscriptions_this_month": new_this_month,
        }
    
    # =========================================================================
    # PAYMENT PROVIDER HELPERS
    # =========================================================================
    
    def _create_razorpay_checkout(
        self,
        user_id: UUID,
        plan: SubscriptionPlan,
        amount: Decimal,
        billing_cycle: str,
        coupon_code: Optional[str],
    ) -> CheckoutResponse:
        """Create Razorpay checkout."""
        # TODO: Integrate with Razorpay API
        raise NotImplementedError("Razorpay integration not yet implemented")
    
    def get_revenue_over_time(self, start_date: datetime) -> dict:
        """
        Get revenue statistics over time.
        
        Args:
            start_date: Start date for the statistics.
            
        Returns:
            Dictionary with revenue data.
        """
        from datetime import timedelta
        
        # Get total revenue from payments
        total_result = self.db.execute(
            select(func.sum(Payment.amount))
            .where(Payment.created_at >= start_date)
            .where(Payment.status == "completed")
        )
        total_revenue = total_result.scalar() or 0
        
        # Get daily revenue - simplified version
        daily_revenue = []
        current_date = start_date
        now = datetime.utcnow()
        
        while current_date < now:
            day_end = current_date + timedelta(days=1)
            day_revenue_result = self.db.execute(
                select(func.sum(Payment.amount))
                .where(Payment.created_at >= current_date)
                .where(Payment.created_at < day_end)
                .where(Payment.status == "completed")
            )
            day_revenue = day_revenue_result.scalar() or 0
            daily_revenue.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "amount": float(day_revenue)
            })
            current_date = day_end
        
        return {
            "total": float(total_revenue),
            "period_start": start_date.isoformat(),
            "period_end": now.isoformat(),
            "daily": daily_revenue
        }
    
    def list_all(
        self,
        status: Optional[str] = None,
        tier: Optional[str] = None,
        plan: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Subscription], int]:
        """
        List all subscriptions with filters (for admin).
        
        Args:
            status: Filter by status
            tier: Filter by subscription tier
            plan: Filter by plan (alias for tier)
            page: Page number
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Tuple of (subscriptions, total_count)
        """
        query = select(Subscription)
        
        # Apply filters
        filters = []
        if status:
            filters.append(Subscription.status == status)
        # plan is an alias for tier
        effective_tier = tier or plan
        if effective_tier:
            filters.append(Subscription.tier == effective_tier)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0
        
        # Apply sorting
        sort_column = getattr(Subscription, sort_by, Subscription.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = self.db.execute(query)
        subscriptions = list(result.scalars().all())
        
        return subscriptions, total


# Dependency injection helper
def get_subscription_service(db: AsyncSession) -> SubscriptionService:
    """Get subscription service instance."""
    return SubscriptionService(db)
