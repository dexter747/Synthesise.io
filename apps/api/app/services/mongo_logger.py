# =============================================================================
# MONGODB LOGGING SERVICE
# =============================================================================
# Handles logging to MongoDB for utility data (analytics, activity, API logs)

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
import logging

from app.core.mongodb import get_mongodb, get_mongodb_sync, Collections

logger = logging.getLogger(__name__)


class MongoLogger:
    """Service for logging utility data to MongoDB."""
    
    # =========================================================================
    # ACTIVITY LOGS
    # =========================================================================
    
    @staticmethod
    async def log_activity(
        user_id: UUID,
        event_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        organization_id: Optional[UUID] = None,
    ):
        """Log user activity to MongoDB."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.ACTIVITY_LOGS].insert_one({
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
                "event_type": event_type,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    @staticmethod
    def log_activity_sync(
        user_id: UUID,
        event_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        organization_id: Optional[UUID] = None,
    ):
        """Log user activity to MongoDB (sync version for Celery)."""
        db = get_mongodb_sync()
        if db is None:
            return
        
        try:
            db[Collections.ACTIVITY_LOGS].insert_one({
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
                "event_type": event_type,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log activity (sync): {e}")
    
    # =========================================================================
    # ANALYTICS EVENTS
    # =========================================================================
    
    @staticmethod
    async def log_analytics_event(
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
    ):
        """Log analytics event to MongoDB."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.ANALYTICS_EVENTS].insert_one({
                "event_name": event_name,
                "properties": properties or {},
                "user_id": str(user_id) if user_id else None,
                "session_id": session_id,
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log analytics event: {e}")
    
    # =========================================================================
    # API REQUEST LOGS
    # =========================================================================
    
    @staticmethod
    async def log_api_request(
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_body: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Log API request to MongoDB."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.API_LOGS].insert_one({
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "user_id": str(user_id) if user_id else None,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "request_body": request_body,
                "error": error,
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    @staticmethod
    async def track_usage(
        user_id: UUID,
        metric: str,
        value: int,
        organization_id: Optional[UUID] = None,
    ):
        """Track usage metrics in MongoDB (aggregated by day)."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            await db[Collections.USAGE_TRACKING].update_one(
                {
                    "user_id": str(user_id),
                    "period": today,
                },
                {
                    "$inc": {f"metrics.{metric}": value},
                    "$setOnInsert": {
                        "organization_id": str(organization_id) if organization_id else None,
                        "created_at": datetime.utcnow(),
                    },
                    "$set": {"updated_at": datetime.utcnow()},
                },
                upsert=True,
            )
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
    
    @staticmethod
    def track_usage_sync(
        user_id: UUID,
        metric: str,
        value: int,
        organization_id: Optional[UUID] = None,
    ):
        """Track usage metrics in MongoDB (sync version for Celery)."""
        db = get_mongodb_sync()
        if db is None:
            return
        
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            db[Collections.USAGE_TRACKING].update_one(
                {
                    "user_id": str(user_id),
                    "period": today,
                },
                {
                    "$inc": {f"metrics.{metric}": value},
                    "$setOnInsert": {
                        "organization_id": str(organization_id) if organization_id else None,
                        "created_at": datetime.utcnow(),
                    },
                    "$set": {"updated_at": datetime.utcnow()},
                },
                upsert=True,
            )
        except Exception as e:
            logger.error(f"Failed to track usage (sync): {e}")
    
    # =========================================================================
    # DATASET DELETION REMINDERS
    # =========================================================================
    
    @staticmethod
    async def schedule_dataset_deletion(
        dataset_id: UUID,
        user_id: UUID,
        dataset_name: str,
        user_email: str,
        deletion_date: datetime,
    ):
        """Schedule a dataset for deletion and reminder."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.DELETION_REMINDERS].insert_one({
                "dataset_id": str(dataset_id),
                "user_id": str(user_id),
                "dataset_name": dataset_name,
                "user_email": user_email,
                "scheduled_deletion_at": deletion_date,
                "reminder_sent": False,
                "reminder_sent_at": None,
                "deleted": False,
                "deleted_at": None,
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to schedule dataset deletion: {e}")
    
    @staticmethod
    def schedule_dataset_deletion_sync(
        dataset_id: UUID,
        user_id: UUID,
        dataset_name: str,
        user_email: str,
        deletion_date: datetime,
    ):
        """Schedule a dataset for deletion (sync version)."""
        db = get_mongodb_sync()
        if db is None:
            return
        
        try:
            db[Collections.DELETION_REMINDERS].insert_one({
                "dataset_id": str(dataset_id),
                "user_id": str(user_id),
                "dataset_name": dataset_name,
                "user_email": user_email,
                "scheduled_deletion_at": deletion_date,
                "reminder_sent": False,
                "reminder_sent_at": None,
                "deleted": False,
                "deleted_at": None,
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to schedule dataset deletion (sync): {e}")
    
    @staticmethod
    def get_pending_reminders_sync(days_before: int = 7) -> List[Dict[str, Any]]:
        """Get datasets that need deletion reminders."""
        db = get_mongodb_sync()
        if db is None:
            return []
        
        try:
            reminder_threshold = datetime.utcnow() + timedelta(days=days_before)
            
            return list(db[Collections.DELETION_REMINDERS].find({
                "reminder_sent": False,
                "deleted": False,
                "scheduled_deletion_at": {"$lte": reminder_threshold},
            }))
        except Exception as e:
            logger.error(f"Failed to get pending reminders: {e}")
            return []
    
    @staticmethod
    def get_datasets_to_delete_sync() -> List[Dict[str, Any]]:
        """Get datasets that are due for deletion."""
        db = get_mongodb_sync()
        if db is None:
            return []
        
        try:
            now = datetime.utcnow()
            
            return list(db[Collections.DELETION_REMINDERS].find({
                "deleted": False,
                "scheduled_deletion_at": {"$lte": now},
            }))
        except Exception as e:
            logger.error(f"Failed to get datasets to delete: {e}")
            return []
    
    @staticmethod
    def mark_reminder_sent_sync(dataset_id: str):
        """Mark reminder as sent for a dataset."""
        db = get_mongodb_sync()
        if db is None:
            return
        
        try:
            db[Collections.DELETION_REMINDERS].update_one(
                {"dataset_id": dataset_id},
                {"$set": {"reminder_sent": True, "reminder_sent_at": datetime.utcnow()}},
            )
        except Exception as e:
            logger.error(f"Failed to mark reminder sent: {e}")
    
    @staticmethod
    def mark_dataset_deleted_sync(dataset_id: str):
        """Mark dataset as deleted."""
        db = get_mongodb_sync()
        if db is None:
            return
        
        try:
            db[Collections.DELETION_REMINDERS].update_one(
                {"dataset_id": dataset_id},
                {"$set": {"deleted": True, "deleted_at": datetime.utcnow()}},
            )
        except Exception as e:
            logger.error(f"Failed to mark dataset deleted: {e}")
    
    # =========================================================================
    # ERROR LOGS
    # =========================================================================
    
    @staticmethod
    async def log_error(
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        user_id: Optional[UUID] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log error to MongoDB."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.ERROR_LOGS].insert_one({
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
                "user_id": str(user_id) if user_id else None,
                "endpoint": endpoint,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    # =========================================================================
    # WEBHOOK LOGS
    # =========================================================================
    
    @staticmethod
    async def log_webhook_delivery(
        webhook_id: UUID,
        event_type: str,
        url: str,
        status_code: Optional[int],
        response_body: Optional[str],
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log webhook delivery attempt to MongoDB."""
        db = get_mongodb()
        if db is None:
            return
        
        try:
            await db[Collections.WEBHOOK_LOGS].insert_one({
                "webhook_id": str(webhook_id),
                "event_type": event_type,
                "url": url,
                "status_code": status_code,
                "response_body": response_body,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to log webhook delivery: {e}")


# Activity event types
class ActivityType:
    LOGIN = "login"
    LOGOUT = "logout"
    DATASET_CREATED = "dataset_created"
    DATASET_DELETED = "dataset_deleted"
    DATASET_DOWNLOADED = "dataset_downloaded"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    GENERATION_FAILED = "generation_failed"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    API_KEY_CREATED = "api_key_created"
    API_KEY_DELETED = "api_key_deleted"
    WEBHOOK_CREATED = "webhook_created"
    WEBHOOK_DELETED = "webhook_deleted"
    TEAM_MEMBER_INVITED = "team_member_invited"
    TEAM_MEMBER_JOINED = "team_member_joined"
    TEAM_MEMBER_REMOVED = "team_member_removed"
    ORGANIZATION_CREATED = "organization_created"
    SETTINGS_UPDATED = "settings_updated"


# Usage metrics
class UsageMetric:
    ROWS_GENERATED = "rows_generated"
    DATASETS_CREATED = "datasets_created"
    API_CALLS = "api_calls"
    DOWNLOADS = "downloads"
    EXPORT_BYTES = "export_bytes"
