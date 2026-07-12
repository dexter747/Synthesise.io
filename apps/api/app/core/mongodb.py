# =============================================================================
# MONGODB CONNECTION
# =============================================================================
# Handles MongoDB connection for utility data (logs, analytics, usage tracking)
# Main data stays in PostgreSQL, MongoDB handles ephemeral/analytical data

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Async MongoDB client (for FastAPI async endpoints)
_async_client: Optional[AsyncIOMotorClient] = None
_async_db: Optional[AsyncIOMotorDatabase] = None

# Sync MongoDB client (for Celery tasks and sync operations)
_sync_client: Optional[MongoClient] = None
_sync_db: Optional[Database] = None


def get_mongodb_url() -> str:
    """Get MongoDB connection URL from settings."""
    return getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')


def get_mongodb_database() -> str:
    """Get MongoDB database name from settings."""
    return getattr(settings, 'MONGODB_DATABASE', 'synthesize_utility')


# =============================================================================
# ASYNC CLIENT (For FastAPI)
# =============================================================================

async def connect_mongodb():
    """Connect to MongoDB asynchronously."""
    global _async_client, _async_db
    
    try:
        mongodb_url = get_mongodb_url()
        database_name = get_mongodb_database()
        
        _async_client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        _async_db = _async_client[database_name]
        
        # Verify connection
        await _async_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {database_name}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise - allow app to run without MongoDB
        _async_client = None
        _async_db = None


async def disconnect_mongodb():
    """Disconnect from MongoDB."""
    global _async_client, _async_db
    
    if _async_client:
        _async_client.close()
        _async_client = None
        _async_db = None
        logger.info("Disconnected from MongoDB")


def get_mongodb() -> Optional[AsyncIOMotorDatabase]:
    """Get async MongoDB database instance."""
    return _async_db


async def get_mongo_db():
    """FastAPI dependency for MongoDB database."""
    if _async_db is None:
        await connect_mongodb()
    return _async_db


# =============================================================================
# SYNC CLIENT (For Celery tasks)
# =============================================================================

def connect_mongodb_sync():
    """Connect to MongoDB synchronously (for Celery tasks)."""
    global _sync_client, _sync_db
    
    try:
        mongodb_url = get_mongodb_url()
        database_name = get_mongodb_database()
        
        _sync_client = MongoClient(
            mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        _sync_db = _sync_client[database_name]
        
        # Verify connection
        _sync_client.admin.command('ping')
        logger.info(f"Connected to MongoDB (sync): {database_name}")
        
        # Create indexes
        create_indexes_sync()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB (sync): {e}")
        _sync_client = None
        _sync_db = None


def get_mongodb_sync() -> Optional[Database]:
    """Get sync MongoDB database instance."""
    global _sync_db
    if _sync_db is None:
        connect_mongodb_sync()
    return _sync_db


# =============================================================================
# INDEXES
# =============================================================================

async def create_indexes():
    """Create indexes for MongoDB collections."""
    if _async_db is None:
        return
    
    try:
        # Activity logs - index by user, timestamp, type
        await _async_db.activity_logs.create_index([("user_id", 1), ("created_at", -1)])
        await _async_db.activity_logs.create_index([("event_type", 1), ("created_at", -1)])
        await _async_db.activity_logs.create_index([("created_at", 1)], expireAfterSeconds=90 * 24 * 60 * 60)  # 90 days TTL
        
        # Usage tracking - index by user, period
        await _async_db.usage_tracking.create_index([("user_id", 1), ("period", 1)])
        await _async_db.usage_tracking.create_index([("organization_id", 1), ("period", 1)])
        
        # Analytics events - index by user, event, timestamp
        await _async_db.analytics_events.create_index([("user_id", 1), ("created_at", -1)])
        await _async_db.analytics_events.create_index([("event_name", 1), ("created_at", -1)])
        await _async_db.analytics_events.create_index([("created_at", 1)], expireAfterSeconds=365 * 24 * 60 * 60)  # 1 year TTL
        
        # API request logs - index by user, endpoint, timestamp
        await _async_db.api_logs.create_index([("user_id", 1), ("created_at", -1)])
        await _async_db.api_logs.create_index([("endpoint", 1), ("method", 1), ("created_at", -1)])
        await _async_db.api_logs.create_index([("created_at", 1)], expireAfterSeconds=30 * 24 * 60 * 60)  # 30 days TTL
        
        # Dataset expiration reminders
        await _async_db.deletion_reminders.create_index([("user_id", 1), ("dataset_id", 1)])
        await _async_db.deletion_reminders.create_index([("scheduled_deletion_at", 1)])
        await _async_db.deletion_reminders.create_index([("reminder_sent", 1), ("scheduled_deletion_at", 1)])
        
        logger.info("MongoDB indexes created")
        
    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {e}")


def create_indexes_sync():
    """Create indexes for MongoDB collections (sync version)."""
    if _sync_db is None:
        return
    
    try:
        # Activity logs
        _sync_db.activity_logs.create_index([("user_id", 1), ("created_at", -1)])
        _sync_db.activity_logs.create_index([("event_type", 1), ("created_at", -1)])
        _sync_db.activity_logs.create_index([("created_at", 1)], expireAfterSeconds=90 * 24 * 60 * 60)
        
        # Usage tracking
        _sync_db.usage_tracking.create_index([("user_id", 1), ("period", 1)])
        _sync_db.usage_tracking.create_index([("organization_id", 1), ("period", 1)])
        
        # Analytics events
        _sync_db.analytics_events.create_index([("user_id", 1), ("created_at", -1)])
        _sync_db.analytics_events.create_index([("event_name", 1), ("created_at", -1)])
        _sync_db.analytics_events.create_index([("created_at", 1)], expireAfterSeconds=365 * 24 * 60 * 60)
        
        # API logs
        _sync_db.api_logs.create_index([("user_id", 1), ("created_at", -1)])
        _sync_db.api_logs.create_index([("endpoint", 1), ("method", 1), ("created_at", -1)])
        _sync_db.api_logs.create_index([("created_at", 1)], expireAfterSeconds=30 * 24 * 60 * 60)
        
        # Deletion reminders
        _sync_db.deletion_reminders.create_index([("user_id", 1), ("dataset_id", 1)])
        _sync_db.deletion_reminders.create_index([("scheduled_deletion_at", 1)])
        
        logger.info("MongoDB indexes created (sync)")
        
    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes (sync): {e}")


# =============================================================================
# COLLECTIONS
# =============================================================================

class Collections:
    """MongoDB collection names."""
    ACTIVITY_LOGS = "activity_logs"
    USAGE_TRACKING = "usage_tracking"
    ANALYTICS_EVENTS = "analytics_events"
    API_LOGS = "api_logs"
    DELETION_REMINDERS = "deletion_reminders"
    ERROR_LOGS = "error_logs"
    WEBHOOK_LOGS = "webhook_logs"
