"""
Activity logging service for Synthesize.io API.

Tracks team activities for audit trails and collaboration awareness.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from enum import Enum

from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import Session, selectinload

import logging

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    """Types of tracked activities."""
    # Dataset activities
    DATASET_CREATED = "dataset.created"
    DATASET_UPDATED = "dataset.updated"
    DATASET_DELETED = "dataset.deleted"
    DATASET_SHARED = "dataset.shared"
    DATASET_UNSHARED = "dataset.unshared"
    DATASET_EXPORTED = "dataset.exported"
    DATASET_GENERATED = "dataset.generated"
    
    # Organization activities
    ORG_CREATED = "organization.created"
    ORG_UPDATED = "organization.updated"
    ORG_SETTINGS_CHANGED = "organization.settings_changed"
    
    # Member activities
    MEMBER_ADDED = "member.added"
    MEMBER_REMOVED = "member.removed"
    MEMBER_ROLE_CHANGED = "member.role_changed"
    MEMBER_LEFT = "member.left"
    
    # Invite activities
    INVITE_SENT = "invite.sent"
    INVITE_ACCEPTED = "invite.accepted"
    INVITE_DECLINED = "invite.declined"
    INVITE_CANCELED = "invite.canceled"
    INVITE_EXPIRED = "invite.expired"
    
    # API key activities
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    
    # Export activities
    EXPORT_STARTED = "export.started"
    EXPORT_COMPLETED = "export.completed"
    EXPORT_FAILED = "export.failed"
    
    # Access activities
    DATASET_ACCESSED = "dataset.accessed"
    DATASET_DOWNLOADED = "dataset.downloaded"


class ActivityService:
    """
    Service for logging and retrieving team activities.
    
    Activities are stored in MongoDB for flexibility and
    can be queried by user, organization, resource, etc.
    """
    
    def __init__(self, db: Session, mongodb=None):
        self.db = db
        self.mongodb = mongodb
    
    async def log_activity(
        self,
        activity_type: ActivityType,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        resource_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log an activity event.
        
        Args:
            activity_type: Type of activity
            user_id: ID of user performing the action
            organization_id: Organization context (if applicable)
            resource_type: Type of resource (dataset, member, etc.)
            resource_id: ID of the affected resource
            resource_name: Human-readable name of resource
            metadata: Additional activity-specific data
            user_agent: Request user agent
            
        Returns:
            Created activity document
        """
        activity = {
            "type": activity_type.value,
            "user_id": str(user_id),
            "organization_id": str(organization_id) if organization_id else None,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "resource_name": resource_name,
            "metadata": metadata or {},
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
        }
        
        # Store in MongoDB if available
        if self.mongodb:
            try:
                result = await self.mongodb.activities.insert_one(activity)
                activity["_id"] = str(result.inserted_id)
            except Exception as e:
                logger.error(f"Failed to log activity to MongoDB: {e}")
        
        # Also log to application logs for debugging
        logger.info(
            f"Activity: {activity_type.value} by user {user_id} "
            f"on {resource_type}:{resource_id}"
        )
        
        return activity
    
    def log_activity_sync(
        self,
        activity_type: Union[ActivityType, str],
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        resource_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous version of log_activity for non-async contexts.
        """
        # Handle both enum and string types
        type_value = activity_type.value if isinstance(activity_type, ActivityType) else activity_type
        
        activity = {
            "type": type_value,
            "user_id": str(user_id),
            "organization_id": str(organization_id) if organization_id else None,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "resource_name": resource_name,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }
        
        logger.info(
            f"Activity: {type_value} by user {user_id} "
            f"on {resource_type}:{resource_id}"
        )
        
        return activity
    
    def get_recent_activities(
        self,
        organization_id: UUID,
        hours: int = 1,
        offset_hours: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get activities within a time range (synchronous version).
        
        Args:
            organization_id: Organization to query
            hours: Number of hours back to look
            offset_hours: Number of hours to offset the start (for looking at older windows)
            
        Returns:
            List of activities (empty if MongoDB not available)
        """
        # For synchronous contexts without MongoDB, return empty list
        # This is a simple implementation that could be enhanced with SQL storage
        logger.info(f"get_recent_activities called for org {organization_id}, hours={hours}")
        return []
    
    async def get_organization_activities(
        self,
        organization_id: UUID,
        activity_types: Optional[List[ActivityType]] = None,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Get activities for an organization.
        
        Args:
            organization_id: Organization to query
            activity_types: Filter by activity types
            user_id: Filter by user
            resource_type: Filter by resource type
            start_date: Filter by date range start
            end_date: Filter by date range end
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (activities list, total count)
        """
        if not self.mongodb:
            return [], 0
        
        # Build query
        query: Dict[str, Any] = {
            "organization_id": str(organization_id)
        }
        
        if activity_types:
            query["type"] = {"$in": [t.value for t in activity_types]}
        
        if user_id:
            query["user_id"] = str(user_id)
        
        if resource_type:
            query["resource_type"] = resource_type
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        try:
            # Get total count
            total = await self.mongodb.activities.count_documents(query)
            
            # Get paginated results
            cursor = (
                self.mongodb.activities
                .find(query)
                .sort("created_at", -1)
                .skip((page - 1) * per_page)
                .limit(per_page)
            )
            
            activities = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                activities.append(doc)
            
            return activities, total
            
        except Exception as e:
            logger.error(f"Failed to query activities: {e}")
            return [], 0
    
    async def get_user_activities(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get activities performed by a user."""
        if not self.mongodb:
            return [], 0
        
        query: Dict[str, Any] = {"user_id": str(user_id)}
        
        if organization_id:
            query["organization_id"] = str(organization_id)
        
        try:
            total = await self.mongodb.activities.count_documents(query)
            
            cursor = (
                self.mongodb.activities
                .find(query)
                .sort("created_at", -1)
                .skip((page - 1) * per_page)
                .limit(per_page)
            )
            
            activities = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                activities.append(doc)
            
            return activities, total
            
        except Exception as e:
            logger.error(f"Failed to query user activities: {e}")
            return [], 0
    
    async def get_resource_activities(
        self,
        resource_type: str,
        resource_id: UUID,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get activities for a specific resource."""
        if not self.mongodb:
            return [], 0
        
        query = {
            "resource_type": resource_type,
            "resource_id": str(resource_id),
        }
        
        try:
            total = await self.mongodb.activities.count_documents(query)
            
            cursor = (
                self.mongodb.activities
                .find(query)
                .sort("created_at", -1)
                .skip((page - 1) * per_page)
                .limit(per_page)
            )
            
            activities = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                activities.append(doc)
            
            return activities, total
            
        except Exception as e:
            logger.error(f"Failed to query resource activities: {e}")
            return [], 0
    
    async def get_activity_summary(
        self,
        organization_id: UUID,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get activity summary statistics for an organization.
        
        Returns counts by activity type, most active users,
        and daily activity trends.
        """
        if not self.mongodb:
            return {
                "total_activities": 0,
                "by_type": {},
                "by_user": [],
                "daily_trend": [],
            }
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            # Aggregation pipeline for summary
            pipeline = [
                {
                    "$match": {
                        "organization_id": str(organization_id),
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$facet": {
                        "by_type": [
                            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                            {"$sort": {"count": -1}}
                        ],
                        "by_user": [
                            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                            {"$sort": {"count": -1}},
                            {"$limit": 10}
                        ],
                        "daily": [
                            {
                                "$group": {
                                    "_id": {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$created_at"
                                        }
                                    },
                                    "count": {"$sum": 1}
                                }
                            },
                            {"$sort": {"_id": 1}}
                        ],
                        "total": [{"$count": "count"}]
                    }
                }
            ]
            
            cursor = self.mongodb.activities.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                result = results[0]
                return {
                    "total_activities": result["total"][0]["count"] if result["total"] else 0,
                    "by_type": {r["_id"]: r["count"] for r in result["by_type"]},
                    "by_user": [
                        {"user_id": r["_id"], "count": r["count"]}
                        for r in result["by_user"]
                    ],
                    "daily_trend": [
                        {"date": r["_id"], "count": r["count"]}
                        for r in result["daily"]
                    ],
                }
            
            return {
                "total_activities": 0,
                "by_type": {},
                "by_user": [],
                "daily_trend": [],
            }
            
        except Exception as e:
            logger.error(f"Failed to get activity summary: {e}")
            return {
                "total_activities": 0,
                "by_type": {},
                "by_user": [],
                "daily_trend": [],
                "error": str(e)
            }


class DatasetAccessService:
    """
    Service for managing shared dataset access within teams.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def share_dataset_with_org(
        self,
        dataset_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        access_level: str = "view",  # view, edit, admin
    ) -> bool:
        """
        Share a dataset with an organization.
        
        Args:
            dataset_id: Dataset to share
            organization_id: Organization to share with
            user_id: User performing the action
            access_level: Access level to grant
            
        Returns:
            True if successful
        """
        from app.models import Dataset
        from app.services.organization_service import OrganizationService
        
        # Get dataset
        result = self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise ValueError("Dataset not found")
        
        # Verify user owns the dataset
        if dataset.user_id != user_id:
            raise PermissionError("Only the dataset owner can share it")
        
        # Verify user is member of the organization
        org_service = OrganizationService(self.db)
        if not org_service.is_member(organization_id, user_id):
            raise PermissionError("You must be a member of the organization")
        
        # Update dataset organization
        dataset.organization_id = organization_id
        dataset.shared_access_level = access_level
        
        self.db.commit()
        
        return True
    
    def unshare_dataset(
        self,
        dataset_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Remove dataset from organization sharing."""
        from app.models import Dataset
        
        result = self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise ValueError("Dataset not found")
        
        if dataset.user_id != user_id:
            raise PermissionError("Only the dataset owner can unshare it")
        
        dataset.organization_id = None
        dataset.shared_access_level = None
        
        self.db.commit()
        
        return True
    
    def get_shared_datasets(
        self,
        organization_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list, int]:
        """
        Get datasets shared with an organization.
        
        Returns datasets the user has access to based on their role.
        """
        from app.models import Dataset
        from app.services.organization_service import OrganizationService
        
        # Verify membership
        org_service = OrganizationService(self.db)
        if not org_service.is_member(organization_id, user_id):
            raise PermissionError("You are not a member of this organization")
        
        # Get shared datasets
        query = (
            select(Dataset)
            .where(Dataset.organization_id == organization_id)
            .where(Dataset.deleted_at.is_(None))
            .order_by(Dataset.updated_at.desc())
        )
        
        count_query = (
            select(func.count(Dataset.id))
            .where(Dataset.organization_id == organization_id)
            .where(Dataset.deleted_at.is_(None))
        )
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        datasets = list(result.scalars().all())
        
        return datasets, total
    
    def check_dataset_access(
        self,
        dataset_id: UUID,
        user_id: UUID,
        required_level: str = "view",
    ) -> bool:
        """
        Check if user has access to a dataset.
        
        Access can be through:
        1. Direct ownership
        2. Organization membership (shared dataset)
        3. Public dataset
        """
        from app.models import Dataset
        from app.services.organization_service import OrganizationService
        
        result = self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            return False
        
        # Owner always has access
        if dataset.user_id == user_id:
            return True
        
        # Public datasets are viewable
        if dataset.is_public and required_level == "view":
            return True
        
        # Check organization access
        if dataset.organization_id:
            org_service = OrganizationService(self.db)
            
            if not org_service.is_member(dataset.organization_id, user_id):
                return False
            
            # Get user's role
            role = org_service.get_member_role(dataset.organization_id, user_id)
            
            access_level = dataset.shared_access_level or "view"
            
            # Role-based access
            if role in ["admin", "owner"]:
                return True  # Admins have full access
            
            if required_level == "view":
                return True  # All members can view
            
            if required_level == "edit" and access_level in ["edit", "admin"]:
                return True
            
            if required_level == "admin" and access_level == "admin":
                return True
        
        return False


class TeamQuotaService:
    """
    Service for managing team-level quotas and usage tracking.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_organization_usage(
        self,
        organization_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get aggregated usage statistics for an organization.
        
        Combines usage from all organization members.
        """
        from app.models import Dataset, GenerationJob, OrganizationMember
        
        # Get all member IDs
        member_result = self.db.execute(
            select(OrganizationMember.user_id)
            .where(OrganizationMember.organization_id == organization_id)
        )
        member_ids = [r[0] for r in member_result.all()]
        
        if not member_ids:
            return {
                "total_datasets": 0,
                "total_rows_generated": 0,
                "total_storage_bytes": 0,
                "member_count": 0,
            }
        
        # Count datasets
        dataset_count = self.db.execute(
            select(func.count(Dataset.id))
            .where(Dataset.user_id.in_(member_ids))
            .where(Dataset.deleted_at.is_(None))
        ).scalar() or 0
        
        # Sum rows generated
        rows_generated = self.db.execute(
            select(func.sum(GenerationJob.row_count))
            .where(GenerationJob.user_id.in_(member_ids))
            .where(GenerationJob.status == "completed")
        ).scalar() or 0
        
        # Sum storage
        storage_bytes = self.db.execute(
            select(func.sum(GenerationJob.file_size))
            .where(GenerationJob.user_id.in_(member_ids))
            .where(GenerationJob.status == "completed")
        ).scalar() or 0
        
        return {
            "total_datasets": dataset_count,
            "total_rows_generated": int(rows_generated),
            "total_storage_bytes": int(storage_bytes),
            "member_count": len(member_ids),
        }
    
    def check_organization_quota(
        self,
        organization_id: UUID,
        quota_type: str,  # datasets, rows, storage
        amount: int = 1,
    ) -> tuple[bool, str]:
        """
        Check if organization has remaining quota.
        
        Returns (is_allowed, message).
        """
        from app.models import Organization
        
        # Get organization and its plan
        result = self.db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            return False, "Organization not found"
        
        # Get plan limits
        plan_limits = self._get_plan_limits(org.plan)
        usage = self.get_organization_usage(organization_id)
        
        if quota_type == "datasets":
            limit = plan_limits.get("max_datasets", float("inf"))
            current = usage["total_datasets"]
            if current + amount > limit:
                return False, f"Organization dataset limit reached ({current}/{limit})"
        
        elif quota_type == "rows":
            limit = plan_limits.get("max_rows_per_month", float("inf"))
            current = usage["total_rows_generated"]
            if current + amount > limit:
                return False, f"Organization row limit reached ({current}/{limit})"
        
        elif quota_type == "storage":
            limit = plan_limits.get("max_storage_bytes", float("inf"))
            current = usage["total_storage_bytes"]
            if current + amount > limit:
                return False, f"Organization storage limit reached"
        
        return True, "Quota available"
    
    def _get_plan_limits(self, plan: str) -> Dict[str, Any]:
        """Get quota limits for a plan.
        
        Updated for 4-tier structure: Free, Pro, Business, Enterprise
        """
        plans = {
            "free": {
                "max_datasets": 5,
                "max_rows_per_month": 10000,
                "max_storage_bytes": 100 * 1024 * 1024,  # 100MB
                "max_members": 1,  # No team in Free
            },
            "pro": {
                "max_datasets": 100,
                "max_rows_per_month": 1000000,  # 1M rows
                "max_storage_bytes": 5 * 1024 * 1024 * 1024,  # 5GB
                "max_members": 1,  # No team in Pro
            },
            "business": {
                "max_datasets": float("inf"),
                "max_rows_per_month": 10000000,  # 10M rows
                "max_storage_bytes": 50 * 1024 * 1024 * 1024,  # 50GB
                "max_members": 10,
            },
            "enterprise": {
                "max_datasets": float("inf"),
                "max_rows_per_month": float("inf"),
                "max_storage_bytes": float("inf"),
                "max_members": float("inf"),
            },
        }
        return plans.get(plan, plans["free"])


def get_activity_service(db: Session, mongodb=None) -> ActivityService:
    """Get activity service instance."""
    return ActivityService(db, mongodb)


def get_dataset_access_service(db: Session) -> DatasetAccessService:
    """Get dataset access service instance."""
    return DatasetAccessService(db)


def get_team_quota_service(db: Session) -> TeamQuotaService:
    """Get team quota service instance."""
    return TeamQuotaService(db)
