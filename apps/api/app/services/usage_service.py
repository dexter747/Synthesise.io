"""
Usage & Quota Service for Synthesize.io
=======================================
Tracks user resource usage and enforces plan-based quotas.

Features:
- Real-time usage tracking (rows, storage, API calls, jobs)
- Quota enforcement per subscription tier
- Usage alerts at 80%, 90%, 100% thresholds
- Monthly reset automation
- Usage history and analytics
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging
import redis
import os
import json

from app.models import (
    User, Subscription, SubscriptionPlan, GenerationRequest,
    SubscriptionTier, SubscriptionStatus
)

logger = logging.getLogger(__name__)

# Redis configuration for caching
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 300  # 5 minutes cache

# Usage thresholds for alerts (percentages)
USAGE_ALERT_THRESHOLDS = [80, 90, 100]


class UsageQuotaExceeded(Exception):
    """Raised when user exceeds their quota"""
    def __init__(self, usage_type: str, limit: int, current: int):
        self.usage_type = usage_type
        self.limit = limit
        self.current = current
        super().__init__(f"{usage_type} quota exceeded: {current}/{limit}")


class UsageService:
    """Service for tracking and enforcing usage quotas"""
    
    # Default quotas per tier (can be overridden by plan settings)
    # 4-tier structure: Beginner, Pro, Business, Enterprise (NO FREE TIER)
    TIER_QUOTAS = {
        SubscriptionTier.BEGINNER: {
            "rows_per_month": 50000,
            "storage_mb": 500,
            "api_calls_per_month": 0,  # No API access for Beginner tier
            "jobs_per_month": 50,
            "max_rows_per_job": 5000,
            "concurrent_jobs": 1
        },
        SubscriptionTier.PRO: {
            "rows_per_month": 1000000,  # 1M rows/month
            "storage_mb": 5000,  # 5GB
            "api_calls_per_month": 10000,
            "jobs_per_month": 500,
            "max_rows_per_job": 100000,  # 100K per job
            "concurrent_jobs": 3
        },
        SubscriptionTier.BUSINESS: {
            "rows_per_month": 10000000,  # 10M rows/month
            "storage_mb": 50000,  # 50GB
            "api_calls_per_month": 100000,
            "jobs_per_month": 2000,
            "max_rows_per_job": 1000000,  # 1M per job
            "concurrent_jobs": 10
        },
        SubscriptionTier.ENTERPRISE: {
            "rows_per_month": -1,  # Unlimited
            "storage_mb": -1,
            "api_calls_per_month": -1,
            "jobs_per_month": -1,
            "max_rows_per_job": -1,
            "concurrent_jobs": -1
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._redis: Optional[redis.Redis] = None
    
    @property
    def redis(self) -> Optional[redis.Redis]:
        """Lazy load Redis connection"""
        if self._redis is None:
            try:
                self._redis = redis.from_url(REDIS_URL, decode_responses=True)
                self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._redis = None
        return self._redis
    
    def _get_cache_key(self, user_id: UUID, key_type: str) -> str:
        """Generate cache key for user usage data"""
        return f"usage:{user_id}:{key_type}"
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached data from Redis"""
        if self.redis:
            try:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            except Exception:
                pass
        return None
    
    def _set_cached(self, key: str, data: Dict, ttl: int = CACHE_TTL) -> None:
        """Set cached data in Redis"""
        if self.redis:
            try:
                self.redis.setex(key, ttl, json.dumps(data))
            except Exception:
                pass
    
    def _invalidate_cache(self, user_id: UUID) -> None:
        """Invalidate all usage cache for a user"""
        if self.redis:
            try:
                keys = [
                    self._get_cache_key(user_id, "current"),
                    self._get_cache_key(user_id, "quotas"),
                    self._get_cache_key(user_id, "summary")
                ]
                self.redis.delete(*keys)
            except Exception:
                pass
    
    def get_user_tier(self, user_id: UUID) -> SubscriptionTier:
        """Get user's current subscription tier"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.PAST_DUE,
                SubscriptionStatus.TRIALING
            ])
        ).first()
        
        if not subscription:
            return SubscriptionTier.BEGINNER
        
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
        
        if not plan:
            return SubscriptionTier.BEGINNER
        
        return plan.tier
    
    def get_user_quotas(self, user_id: UUID) -> Dict[str, int]:
        """Get user's quota limits based on their subscription tier"""
        # Check cache
        cache_key = self._get_cache_key(user_id, "quotas")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        tier = self.get_user_tier(user_id)
        quotas = self.TIER_QUOTAS.get(tier, self.TIER_QUOTAS[SubscriptionTier.BEGINNER]).copy()
        
        # Check for custom limits in subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if subscription and subscription.metadata:
            # Override with custom limits if set
            custom_limits = subscription.metadata.get("custom_limits", {})
            quotas.update(custom_limits)
        
        self._set_cached(cache_key, quotas)
        return quotas
    
    def get_current_usage(self, user_id: UUID) -> Dict[str, int]:
        """Get user's current month usage statistics"""
        # Check cache
        cache_key = self._get_cache_key(user_id, "current")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Calculate current billing period
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count rows generated this month
        rows_result = self.db.query(func.sum(GenerationRequest.row_count)).filter(
            GenerationRequest.user_id == user_id,
            GenerationRequest.created_at >= period_start,
            GenerationRequest.deleted_at.is_(None)
        ).scalar() or 0
        
        # Count jobs this month
        jobs_count = self.db.query(func.count(GenerationRequest.id)).filter(
            GenerationRequest.user_id == user_id,
            GenerationRequest.created_at >= period_start,
            GenerationRequest.deleted_at.is_(None)
        ).scalar() or 0
        
        # Count concurrent (active) jobs
        concurrent_jobs = self.db.query(func.count(GenerationRequest.id)).filter(
            GenerationRequest.user_id == user_id,
            GenerationRequest.status.in_(["pending", "processing"]),
            GenerationRequest.deleted_at.is_(None)
        ).scalar() or 0
        
        # Get API call count from Redis or metadata
        api_calls = self._get_api_call_count(user_id, period_start)
        
        # Calculate storage usage (in MB)
        storage_mb = self._calculate_storage_usage(user_id)
        
        usage = {
            "rows_per_month": int(rows_result),
            "jobs_per_month": jobs_count,
            "concurrent_jobs": concurrent_jobs,
            "api_calls_per_month": api_calls,
            "storage_mb": storage_mb,
            "period_start": period_start.isoformat(),
            "period_end": (period_start + timedelta(days=32)).replace(day=1).isoformat()
        }
        
        self._set_cached(cache_key, usage, ttl=60)  # Cache for 1 minute
        return usage
    
    def _get_api_call_count(self, user_id: UUID, period_start: datetime) -> int:
        """Get API call count from Redis counter"""
        if self.redis:
            try:
                key = f"api_calls:{user_id}:{period_start.strftime('%Y-%m')}"
                count = self.redis.get(key)
                return int(count) if count else 0
            except Exception:
                pass
        return 0
    
    def increment_api_calls(self, user_id: UUID) -> int:
        """Increment API call counter for user"""
        if self.redis:
            try:
                now = datetime.utcnow()
                key = f"api_calls:{user_id}:{now.strftime('%Y-%m')}"
                count = self.redis.incr(key)
                
                # Set expiry to end of month + 1 day
                next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
                ttl = int((next_month - now).total_seconds()) + 86400
                self.redis.expire(key, ttl)
                
                return count
            except Exception as e:
                logger.warning(f"Failed to increment API calls: {e}")
        return 0
    
    def _calculate_storage_usage(self, user_id: UUID) -> int:
        """Calculate user's storage usage in MB"""
        # Sum up file sizes from generated datasets
        # This is a placeholder - actual implementation depends on storage backend
        result = self.db.query(func.sum(GenerationRequest.row_count * 100)).filter(
            GenerationRequest.user_id == user_id,
            GenerationRequest.deleted_at.is_(None)
        ).scalar() or 0
        
        # Rough estimate: ~100 bytes per row
        return int(result / (1024 * 1024))  # Convert to MB
    
    def get_usage_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive usage summary with quotas and percentages"""
        cache_key = self._get_cache_key(user_id, "summary")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        usage = self.get_current_usage(user_id)
        quotas = self.get_user_quotas(user_id)
        tier = self.get_user_tier(user_id)
        
        summary = {
            "tier": tier.value,
            "period_start": usage.get("period_start"),
            "period_end": usage.get("period_end"),
            "usage": {},
            "alerts": []
        }
        
        metrics = [
            ("rows_per_month", "Data Rows"),
            ("jobs_per_month", "Jobs"),
            ("api_calls_per_month", "API Calls"),
            ("storage_mb", "Storage (MB)")
        ]
        
        for metric_key, metric_name in metrics:
            current = usage.get(metric_key, 0)
            limit = quotas.get(metric_key, 0)
            
            if limit == -1:  # Unlimited
                percentage = 0
                remaining = -1
            elif limit == 0:
                percentage = 100 if current > 0 else 0
                remaining = 0
            else:
                percentage = min(100, int((current / limit) * 100))
                remaining = max(0, limit - current)
            
            summary["usage"][metric_key] = {
                "current": current,
                "limit": limit,
                "remaining": remaining,
                "percentage": percentage,
                "name": metric_name,
                "unlimited": limit == -1
            }
            
            # Check for alerts
            if limit != -1 and percentage >= 80:
                for threshold in USAGE_ALERT_THRESHOLDS:
                    if percentage >= threshold:
                        summary["alerts"].append({
                            "type": metric_key,
                            "name": metric_name,
                            "threshold": threshold,
                            "current": current,
                            "limit": limit
                        })
                        break
        
        self._set_cached(cache_key, summary, ttl=60)
        return summary
    
    def check_quota(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int = 1,
        raise_exception: bool = True
    ) -> Dict[str, Any]:
        """
        Check if user has quota available for an operation.
        
        Args:
            user_id: User's UUID
            usage_type: Type of usage (rows_per_month, jobs_per_month, etc.)
            amount: Amount to consume
            raise_exception: Whether to raise exception if quota exceeded
        
        Returns:
            Dict with allowed, current, limit, remaining
        
        Raises:
            UsageQuotaExceeded: If quota exceeded and raise_exception=True
        """
        usage = self.get_current_usage(user_id)
        quotas = self.get_user_quotas(user_id)
        
        current = usage.get(usage_type, 0)
        limit = quotas.get(usage_type, 0)
        
        # Unlimited tier
        if limit == -1:
            return {
                "allowed": True,
                "current": current,
                "limit": -1,
                "remaining": -1,
                "unlimited": True
            }
        
        new_total = current + amount
        allowed = new_total <= limit
        
        result = {
            "allowed": allowed,
            "current": current,
            "limit": limit,
            "remaining": max(0, limit - current),
            "requested": amount,
            "would_use": new_total,
            "unlimited": False
        }
        
        if not allowed and raise_exception:
            raise UsageQuotaExceeded(usage_type, limit, current)
        
        return result
    
    def check_row_quota(self, user_id: UUID, row_count: int) -> Dict[str, Any]:
        """Check if user can generate specified number of rows"""
        # Check monthly quota
        monthly_check = self.check_quota(
            user_id, "rows_per_month", row_count, raise_exception=False
        )
        
        if not monthly_check["allowed"]:
            raise UsageQuotaExceeded(
                "rows_per_month",
                monthly_check["limit"],
                monthly_check["current"]
            )
        
        # Check per-job limit
        quotas = self.get_user_quotas(user_id)
        max_per_job = quotas.get("max_rows_per_job", 0)
        
        if max_per_job != -1 and row_count > max_per_job:
            raise UsageQuotaExceeded(
                "max_rows_per_job",
                max_per_job,
                row_count
            )
        
        return monthly_check
    
    def check_job_quota(self, user_id: UUID) -> Dict[str, Any]:
        """Check if user can create a new job"""
        # Check monthly jobs quota
        monthly_check = self.check_quota(
            user_id, "jobs_per_month", 1, raise_exception=False
        )
        
        if not monthly_check["allowed"]:
            raise UsageQuotaExceeded(
                "jobs_per_month",
                monthly_check["limit"],
                monthly_check["current"]
            )
        
        # Check concurrent jobs
        usage = self.get_current_usage(user_id)
        quotas = self.get_user_quotas(user_id)
        
        concurrent = usage.get("concurrent_jobs", 0)
        max_concurrent = quotas.get("concurrent_jobs", 1)
        
        if max_concurrent != -1 and concurrent >= max_concurrent:
            raise UsageQuotaExceeded(
                "concurrent_jobs",
                max_concurrent,
                concurrent
            )
        
        return monthly_check
    
    def record_usage(
        self,
        user_id: UUID,
        usage_type: str,
        amount: int,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Record usage for billing and analytics.
        Called after successful operations.
        """
        self._invalidate_cache(user_id)
        
        # Check for threshold alerts
        summary = self.get_usage_summary(user_id)
        usage_data = summary["usage"].get(usage_type, {})
        percentage = usage_data.get("percentage", 0)
        
        # Send alerts if crossing thresholds
        for threshold in USAGE_ALERT_THRESHOLDS:
            if percentage >= threshold:
                self._send_usage_alert(
                    user_id,
                    usage_type,
                    percentage,
                    usage_data.get("limit", 0),
                    usage_data.get("current", 0)
                )
                break
    
    def _send_usage_alert(
        self,
        user_id: UUID,
        usage_type: str,
        percentage: int,
        limit: int,
        current: int
    ) -> None:
        """Send usage alert notification"""
        # Check if alert already sent this period
        if self.redis:
            alert_key = f"usage_alert:{user_id}:{usage_type}:{percentage}"
            if self.redis.get(alert_key):
                return  # Alert already sent
            
            # Mark alert as sent (expires at end of month)
            now = datetime.utcnow()
            next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
            ttl = int((next_month - now).total_seconds())
            self.redis.setex(alert_key, ttl, "1")
        
        # Queue email notification
        try:
            from app.tasks.notifications import send_usage_warning_email
            send_usage_warning_email.delay(
                str(user_id),
                usage_type,
                percentage,
                limit,
                current
            )
        except Exception as e:
            logger.error(f"Failed to send usage alert: {e}")
    
    def get_usage_history(
        self,
        user_id: UUID,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """Get historical usage data for specified number of months"""
        now = datetime.utcnow()
        history = []
        
        for i in range(months):
            month_start = (now - timedelta(days=30 * i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            # Get rows generated
            rows = self.db.query(func.sum(GenerationRequest.row_count)).filter(
                GenerationRequest.user_id == user_id,
                GenerationRequest.created_at >= month_start,
                GenerationRequest.created_at < month_end,
                GenerationRequest.deleted_at.is_(None)
            ).scalar() or 0
            
            # Get job count
            jobs = self.db.query(func.count(GenerationRequest.id)).filter(
                GenerationRequest.user_id == user_id,
                GenerationRequest.created_at >= month_start,
                GenerationRequest.created_at < month_end,
                GenerationRequest.deleted_at.is_(None)
            ).scalar() or 0
            
            history.append({
                "month": month_start.strftime("%Y-%m"),
                "month_name": month_start.strftime("%B %Y"),
                "rows_generated": int(rows),
                "jobs_created": jobs
            })
        
        return list(reversed(history))


def get_usage_service(db: Session) -> UsageService:
    """Factory function to get UsageService instance"""
    return UsageService(db)
