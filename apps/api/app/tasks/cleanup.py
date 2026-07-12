"""
Cleanup and maintenance tasks - Scheduled periodic jobs
"""
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.mongodb import get_mongodb_sync
from app.services.mongo_logger import MongoLogger, ActivityType
from app.utils.email import send_email
from app.models import Dataset, User
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import and_
import os
import logging

logger = logging.getLogger(__name__)

# Dataset retention period in days
DATASET_RETENTION_DAYS = 30
# Days before deletion to send reminder
REMINDER_DAYS_BEFORE = 7


@celery_app.task(name="app.tasks.cleanup.cleanup_old_datasets")
def cleanup_old_datasets() -> Dict[str, Any]:
    """
    Delete datasets older than retention period (30 days).
    Also schedules reminders to be sent 7 days before deletion.
    Runs daily via Celery Beat.
    """
    logger.info("Running dataset cleanup task")
    
    db = SessionLocal()
    deleted_count = 0
    scheduled_count = 0
    
    try:
        # Get datasets that are due for deletion (past retention period)
        cutoff_date = datetime.utcnow() - timedelta(days=DATASET_RETENTION_DAYS)
        
        old_datasets = db.query(Dataset).filter(
            Dataset.created_at < cutoff_date
        ).all()
        
        for dataset in old_datasets:
            try:
                # Get user email for notification
                user = db.query(User).filter(User.id == dataset.user_id).first()
                
                # Delete files if they exist
                if dataset.file_path and os.path.exists(dataset.file_path):
                    os.remove(dataset.file_path)
                    logger.info(f"Deleted file: {dataset.file_path}")
                
                # Delete from database
                db.delete(dataset)
                db.commit()
                deleted_count += 1
                
                # Log activity
                MongoLogger.log_activity_sync(
                    user_id=dataset.user_id,
                    event_type=ActivityType.DATASET_DELETED,
                    description=f"Dataset '{dataset.name}' auto-deleted after {DATASET_RETENTION_DAYS} days",
                    metadata={"dataset_id": str(dataset.id), "auto_delete": True}
                )
                
                # Mark as deleted in MongoDB
                MongoLogger.mark_dataset_deleted_sync(str(dataset.id))
                
                # Send deletion notification
                if user and user.email:
                    send_email(
                        to_email=user.email,
                        subject="Your dataset has been deleted",
                        template_name="dataset_deleted",
                        template_data={
                            "user_name": user.name or "User",
                            "dataset_name": dataset.name,
                            "deleted_at": datetime.utcnow().strftime("%B %d, %Y"),
                        }
                    )
                
            except Exception as e:
                logger.error(f"Failed to delete dataset {dataset.id}: {e}")
                db.rollback()
        
        # Schedule reminders for datasets approaching deletion
        reminder_threshold = datetime.utcnow() - timedelta(days=DATASET_RETENTION_DAYS - REMINDER_DAYS_BEFORE)
        
        datasets_needing_reminder = db.query(Dataset).join(User).filter(
            and_(
                Dataset.created_at < reminder_threshold,
                Dataset.created_at >= cutoff_date
            )
        ).all()
        
        for dataset in datasets_needing_reminder:
            try:
                user = db.query(User).filter(User.id == dataset.user_id).first()
                if user:
                    deletion_date = dataset.created_at + timedelta(days=DATASET_RETENTION_DAYS)
                    
                    # Schedule in MongoDB if not already scheduled
                    MongoLogger.schedule_dataset_deletion_sync(
                        dataset_id=dataset.id,
                        user_id=user.id,
                        dataset_name=dataset.name,
                        user_email=user.email,
                        deletion_date=deletion_date,
                    )
                    scheduled_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to schedule reminder for dataset {dataset.id}: {e}")
        
    finally:
        db.close()
    
    logger.info(f"Dataset cleanup complete: {deleted_count} deleted, {scheduled_count} scheduled for reminder")
    
    return {
        "deleted_count": deleted_count,
        "scheduled_count": scheduled_count,
    }


@celery_app.task(name="app.tasks.cleanup.send_deletion_reminders")
def send_deletion_reminders() -> Dict[str, Any]:
    """
    Send email reminders to users about upcoming dataset deletions.
    Runs daily via Celery Beat.
    """
    logger.info("Sending deletion reminders")
    
    reminders_sent = 0
    
    # Get pending reminders from MongoDB
    pending = MongoLogger.get_pending_reminders_sync(days_before=REMINDER_DAYS_BEFORE)
    
    for reminder in pending:
        try:
            days_until = (reminder["scheduled_deletion_at"] - datetime.utcnow()).days
            
            send_email(
                to_email=reminder["user_email"],
                subject=f"Your dataset will be deleted in {days_until} days",
                template_name="dataset_deletion_reminder",
                template_data={
                    "user_name": "User",
                    "dataset_name": reminder["dataset_name"],
                    "days_until_deletion": max(1, days_until),
                    "deletion_date": reminder["scheduled_deletion_at"].strftime("%B %d, %Y"),
                    "download_url": f"/datasets/{reminder['dataset_id']}",
                }
            )
            
            # Mark reminder as sent
            MongoLogger.mark_reminder_sent_sync(reminder["dataset_id"])
            reminders_sent += 1
            
        except Exception as e:
            logger.error(f"Failed to send reminder for dataset {reminder.get('dataset_id')}: {e}")
    
    logger.info(f"Sent {reminders_sent} deletion reminders")
    
    return {"reminders_sent": reminders_sent}


@celery_app.task(name="app.tasks.cleanup.calculate_usage_stats")
def calculate_usage_stats() -> Dict[str, Any]:
    """
    Calculate and cache usage statistics for dashboard.
    Runs every 30 minutes via Celery Beat.
    """
    logger.info("Calculating usage statistics")
    
    db = SessionLocal()
    users_processed = 0
    
    try:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            try:
                # Count datasets
                datasets_count = db.query(Dataset).filter(
                    Dataset.user_id == user.id
                ).count()
                
                # Track in MongoDB
                MongoLogger.track_usage_sync(
                    user_id=user.id,
                    metric="datasets_count",
                    value=datasets_count,
                )
                
                users_processed += 1
                
            except Exception as e:
                logger.error(f"Failed to calculate stats for user {user.id}: {e}")
        
    finally:
        db.close()
    
    return {
        "users_processed": users_processed,
        "stats_updated": True
    }


@celery_app.task(name="app.tasks.cleanup.archive_old_jobs")
def archive_old_jobs() -> Dict[str, Any]:
    """
    Archive completed jobs older than 30 days.
    """
    logger.info("Archiving old jobs")
    
    # Jobs are tracked in MongoDB with TTL indexes
    # This task is for any additional PostgreSQL cleanup
    
    return {
        "archived_count": 0
    }


# =============================================================================
# SUBSCRIPTION EXPIRY TASKS
# =============================================================================

GRACE_PERIOD_DAYS = 7


@celery_app.task(name="app.tasks.cleanup.check_subscription_expiry")
def check_subscription_expiry() -> Dict[str, Any]:
    """
    Check for expired subscriptions and handle grace periods.
    Runs daily via Celery Beat.
    
    Flow:
    1. Find subscriptions where current_period_end has passed
    2. If within grace period (7 days), mark as ON_HOLD
    3. If past grace period, mark as EXPIRED
    4. Send appropriate notifications
    """
    from app.models import Subscription, SubscriptionStatus, User
    
    logger.info("Checking subscription expiry")
    
    db = SessionLocal()
    expired_count = 0
    on_hold_count = 0
    
    try:
        now = datetime.utcnow()
        grace_period_cutoff = now - timedelta(days=GRACE_PERIOD_DAYS)
        
        # Find subscriptions that need attention
        subscriptions = db.query(Subscription).filter(
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.ON_HOLD,
                SubscriptionStatus.PAST_DUE
            ]),
            Subscription.current_period_end < now
        ).all()
        
        for sub in subscriptions:
            user = db.query(User).filter(User.id == sub.user_id).first()
            
            # Check if past grace period
            if sub.current_period_end < grace_period_cutoff:
                # Expire the subscription
                sub.status = SubscriptionStatus.EXPIRED
                expired_count += 1
                
                logger.info(f"Expired subscription {sub.id} for user {sub.user_id}")
                
                # Send expiry notification
                if user and user.email:
                    try:
                        send_email(
                            to_email=user.email,
                            subject="Your Synthesize.io subscription has expired",
                            template_name="subscription_expired",
                            template_data={
                                "user_name": user.first_name or "User",
                                "plan_name": "Your Plan",
                                "expired_at": sub.current_period_end.strftime("%B %d, %Y"),
                                "reactivate_url": "https://synthesize.io/pricing",
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to send expiry email: {e}")
                
            elif sub.status == SubscriptionStatus.ACTIVE:
                # Move to on_hold (within grace period)
                sub.status = SubscriptionStatus.ON_HOLD
                on_hold_count += 1
                
                days_remaining = (grace_period_cutoff - sub.current_period_end).days + GRACE_PERIOD_DAYS
                
                logger.info(f"Subscription {sub.id} moved to ON_HOLD, {days_remaining} days until expiry")
                
                # Send grace period notification
                if user and user.email:
                    try:
                        send_email(
                            to_email=user.email,
                            subject="Action required: Your subscription payment failed",
                            template_name="subscription_on_hold",
                            template_data={
                                "user_name": user.first_name or "User",
                                "days_remaining": max(1, days_remaining),
                                "update_payment_url": "https://synthesize.io/settings/billing",
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to send on_hold email: {e}")
        
        db.commit()
        
    finally:
        db.close()
    
    logger.info(f"Subscription expiry check complete: {expired_count} expired, {on_hold_count} on hold")
    
    return {
        "expired_count": expired_count,
        "on_hold_count": on_hold_count,
    }


@celery_app.task(name="app.tasks.cleanup.send_subscription_reminders")
def send_subscription_reminders() -> Dict[str, Any]:
    """
    Send reminders to users whose subscriptions are about to expire.
    Runs daily via Celery Beat.
    
    Sends reminders at:
    - 7 days before expiry
    - 3 days before expiry
    - 1 day before expiry
    """
    from app.models import Subscription, SubscriptionStatus, User
    
    logger.info("Sending subscription renewal reminders")
    
    db = SessionLocal()
    reminders_sent = 0
    
    try:
        now = datetime.utcnow()
        
        # Reminder thresholds (days before expiry)
        reminder_days = [7, 3, 1]
        
        for days in reminder_days:
            # Find subscriptions expiring in exactly 'days' days
            expiry_start = now + timedelta(days=days)
            expiry_end = now + timedelta(days=days + 1)
            
            subscriptions = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end >= expiry_start,
                Subscription.current_period_end < expiry_end
            ).all()
            
            for sub in subscriptions:
                user = db.query(User).filter(User.id == sub.user_id).first()
                
                if user and user.email:
                    try:
                        send_email(
                            to_email=user.email,
                            subject=f"Your subscription renews in {days} day{'s' if days > 1 else ''}",
                            template_name="subscription_renewal_reminder",
                            template_data={
                                "user_name": user.first_name or "User",
                                "days_until_renewal": days,
                                "renewal_date": sub.current_period_end.strftime("%B %d, %Y"),
                                "manage_subscription_url": "https://synthesize.io/settings/billing",
                            }
                        )
                        reminders_sent += 1
                    except Exception as e:
                        logger.error(f"Failed to send renewal reminder: {e}")
        
    finally:
        db.close()
    
    logger.info(f"Sent {reminders_sent} subscription renewal reminders")
    
    return {"reminders_sent": reminders_sent}
