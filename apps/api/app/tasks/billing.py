"""
Billing and Subscription Tasks
==============================
Scheduled tasks for subscription management, renewal reminders,
grace period enforcement, and payment retries.
"""
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import (
    Subscription, SubscriptionPlan, User, Payment, Invoice,
    SubscriptionStatus, PaymentStatus, PaymentProvider
)
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import and_, or_
import logging
import os

logger = logging.getLogger(__name__)

# Configuration
RENEWAL_REMINDER_DAYS = [7, 3, 1]  # Days before expiry to send reminders
GRACE_PERIOD_DAYS = 7
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAYS = [1, 3, 7]  # Days between retries


@celery_app.task(name="app.tasks.billing.check_expiring_subscriptions")
def check_expiring_subscriptions() -> Dict[str, Any]:
    """
    Check for subscriptions expiring soon and send renewal reminders.
    Runs daily via Celery Beat.
    """
    logger.info("Checking for expiring subscriptions")
    
    db = SessionLocal()
    reminders_sent = 0
    
    try:
        now = datetime.utcnow()
        
        for days in RENEWAL_REMINDER_DAYS:
            target_date = now + timedelta(days=days)
            # Find subscriptions expiring on this day
            expiring = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end >= target_date.replace(hour=0, minute=0, second=0),
                Subscription.current_period_end < target_date.replace(hour=23, minute=59, second=59)
            ).all()
            
            for subscription in expiring:
                try:
                    user = db.query(User).filter(User.id == subscription.user_id).first()
                    if user:
                        from app.tasks.notifications import send_subscription_expiring_email
                        send_subscription_expiring_email.delay(str(user.id), days)
                        reminders_sent += 1
                        logger.info(f"Sent {days}-day expiry reminder to user {user.id}")
                except Exception as e:
                    logger.error(f"Failed to send expiry reminder: {e}")
        
        return {
            "status": "completed",
            "reminders_sent": reminders_sent
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.process_grace_period_expirations")
def process_grace_period_expirations() -> Dict[str, Any]:
    """
    Process subscriptions whose grace period has expired.
    Downgrades them to free tier.
    Runs daily via Celery Beat.
    """
    logger.info("Processing grace period expirations")
    
    db = SessionLocal()
    expired_count = 0
    
    try:
        now = datetime.utcnow()
        
        # Find subscriptions past due with expired grace period
        past_due_subscriptions = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.PAST_DUE
        ).all()
        
        for subscription in past_due_subscriptions:
            if subscription.metadata and subscription.metadata.get("grace_period_end"):
                grace_end = datetime.fromisoformat(subscription.metadata["grace_period_end"])
                
                if now > grace_end:
                    # Grace period expired - expire subscription
                    subscription.status = SubscriptionStatus.EXPIRED
                    subscription.metadata["expired_reason"] = "grace_period_ended"
                    subscription.metadata["expired_at"] = now.isoformat()
                    
                    # Create free subscription
                    free_plan = db.query(SubscriptionPlan).filter(
                        SubscriptionPlan.slug == "free"
                    ).first()
                    
                    if free_plan:
                        subscription.plan_id = free_plan.id
                        subscription.status = SubscriptionStatus.ACTIVE
                    
                    db.commit()
                    expired_count += 1
                    
                    # Notify user
                    user = db.query(User).filter(User.id == subscription.user_id).first()
                    if user:
                        from app.tasks.notifications import send_subscription_cancelled_email
                        send_subscription_cancelled_email.delay(
                            str(user.id),
                            now.strftime("%B %d, %Y")
                        )
                    
                    logger.info(f"Expired subscription {subscription.id} after grace period")
        
        return {
            "status": "completed",
            "expired_count": expired_count
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.retry_failed_payments")
def retry_failed_payments() -> Dict[str, Any]:
    """
    Automatically retry failed payments based on retry schedule.
    Runs daily via Celery Beat.
    """
    logger.info("Retrying failed payments")
    
    db = SessionLocal()
    retried_count = 0
    
    try:
        now = datetime.utcnow()
        
        # Find subscriptions with pending retries
        past_due = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.PAST_DUE
        ).all()
        
        for subscription in past_due:
            if not subscription.metadata:
                continue
            
            retry_count = subscription.metadata.get("retry_count", 0)
            last_retry = subscription.metadata.get("last_retry_at")
            
            if retry_count >= MAX_RETRY_ATTEMPTS:
                continue  # Max retries reached
            
            # Check if it's time for next retry
            if last_retry:
                last_retry_date = datetime.fromisoformat(last_retry)
                days_since_retry = (now - last_retry_date).days
                
                if retry_count < len(RETRY_DELAYS):
                    next_retry_delay = RETRY_DELAYS[retry_count]
                    if days_since_retry < next_retry_delay:
                        continue  # Not time yet
            
            # Attempt payment retry
            try:
                plan = db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.id == subscription.plan_id
                ).first()
                
                if not plan:
                    continue
                
                user = db.query(User).filter(User.id == subscription.user_id).first()
                if not user:
                    continue
                
                # Queue payment retry task
                retry_payment_for_subscription.delay(
                    str(subscription.id),
                    str(plan.id),
                    subscription.payment_provider.value if subscription.payment_provider else "dodo"
                )
                
                retried_count += 1
                logger.info(f"Queued payment retry for subscription {subscription.id}")
                
            except Exception as e:
                logger.error(f"Failed to queue payment retry: {e}")
        
        return {
            "status": "completed",
            "retried_count": retried_count
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.retry_payment_for_subscription")
def retry_payment_for_subscription(
    subscription_id: str,
    plan_id: str,
    payment_provider: str
) -> Dict[str, Any]:
    """
    Retry a specific payment for a subscription.
    """
    logger.info(f"Retrying payment for subscription {subscription_id}")
    
    db = SessionLocal()
    
    try:
        from uuid import UUID
        
        subscription = db.query(Subscription).filter(
            Subscription.id == UUID(subscription_id)
        ).first()
        
        if not subscription:
            return {"status": "failed", "error": "Subscription not found"}
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == UUID(plan_id)
        ).first()
        
        if not plan:
            return {"status": "failed", "error": "Plan not found"}
        
        user = db.query(User).filter(User.id == subscription.user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        # For now, we notify the user to manually retry
        # Full auto-charge requires storing payment methods securely
        from app.tasks.notifications import send_payment_failed_email
        
        retry_count = subscription.metadata.get("retry_count", 0) if subscription.metadata else 0
        next_retry_days = RETRY_DELAYS[min(retry_count, len(RETRY_DELAYS) - 1)]
        
        send_payment_failed_email.delay(
            str(user.id),
            retry_count + 1,
            next_retry_days
        )
        
        # Update retry metadata
        subscription.metadata = subscription.metadata or {}
        subscription.metadata["retry_count"] = retry_count + 1
        subscription.metadata["last_retry_at"] = datetime.utcnow().isoformat()
        
        db.commit()
        
        return {
            "status": "notification_sent",
            "retry_count": retry_count + 1
        }
    except Exception as e:
        logger.error(f"Payment retry failed: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.generate_monthly_invoices")
def generate_monthly_invoices() -> Dict[str, Any]:
    """
    Generate monthly invoices for active subscriptions.
    Runs on the 1st of each month via Celery Beat.
    """
    logger.info("Generating monthly invoices")
    
    db = SessionLocal()
    generated_count = 0
    
    try:
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Find active paid subscriptions
        active_subscriptions = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).all()
        
        for subscription in active_subscriptions:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
            
            if not plan or plan.slug == "free":
                continue  # Skip free plans
            
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if not user:
                continue
            
            # Check if invoice already exists for this month
            existing_invoice = db.query(Invoice).filter(
                Invoice.subscription_id == subscription.id,
                Invoice.invoice_date >= month_start.date()
            ).first()
            
            if existing_invoice:
                continue  # Invoice already generated
            
            # Generate invoice
            try:
                from app.api.v1.endpoints.payments import generate_invoice_number
                
                invoice = Invoice(
                    user_id=user.id,
                    subscription_id=subscription.id,
                    invoice_number=generate_invoice_number(db),
                    amount_cents=plan.monthly_price_cents,
                    tax_cents=0,
                    total_cents=plan.monthly_price_cents,
                    currency="USD",
                    status="open",  # Will be marked paid when payment processed
                    line_items=[{
                        "description": f"{plan.name} Subscription - {now.strftime('%B %Y')}",
                        "quantity": 1,
                        "unit_price": plan.monthly_price_cents / 100,
                        "amount": plan.monthly_price_cents / 100
                    }],
                    billing_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email,
                    billing_email=user.email,
                    invoice_date=now.date(),
                    due_date=(now + timedelta(days=7)).date()
                )
                db.add(invoice)
                db.commit()
                generated_count += 1
                
                logger.info(f"Generated invoice {invoice.invoice_number} for user {user.id}")
                
            except Exception as e:
                logger.error(f"Failed to generate invoice: {e}")
                db.rollback()
        
        return {
            "status": "completed",
            "generated_count": generated_count
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.reset_monthly_usage")
def reset_monthly_usage() -> Dict[str, Any]:
    """
    Reset monthly usage counters at the start of each billing period.
    Runs on the 1st of each month via Celery Beat.
    """
    logger.info("Resetting monthly usage counters")
    
    # Usage is calculated dynamically based on dates,
    # so this task mainly clears Redis counters
    
    try:
        import redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, decode_responses=True)
        
        # Get last month's prefix
        now = datetime.utcnow()
        last_month = (now.replace(day=1) - timedelta(days=1))
        old_prefix = f"api_calls:*:{last_month.strftime('%Y-%m')}"
        
        # Delete old API call counters
        keys = list(r.scan_iter(match=old_prefix))
        if keys:
            r.delete(*keys)
            logger.info(f"Deleted {len(keys)} old API call counters")
        
        return {
            "status": "completed",
            "keys_deleted": len(keys) if keys else 0
        }
    except Exception as e:
        logger.error(f"Failed to reset usage counters: {e}")
        return {"status": "failed", "error": str(e)}


# ============================================================================
# CELERY BEAT SCHEDULE ADDITIONS
# ============================================================================

# Add these to celery_app.py beat_schedule:
"""
# Billing tasks - add to CELERY_BEAT_SCHEDULE in celery_app.py
'check-expiring-subscriptions': {
    'task': 'app.tasks.billing.check_expiring_subscriptions',
    'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
},
'process-grace-period-expirations': {
    'task': 'app.tasks.billing.process_grace_period_expirations',
    'schedule': crontab(hour=0, minute=0),  # Daily at midnight
},
'retry-failed-payments': {
    'task': 'app.tasks.billing.retry_failed_payments',
    'schedule': crontab(hour=10, minute=0),  # Daily at 10 AM
},
'generate-monthly-invoices': {
    'task': 'app.tasks.billing.generate_monthly_invoices',
    'schedule': crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
},
'reset-monthly-usage': {
    'task': 'app.tasks.billing.reset_monthly_usage',
    'schedule': crontab(hour=0, minute=5, day_of_month=1),  # 1st of month
},
"""
