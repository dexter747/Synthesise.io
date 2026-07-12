"""
Quota Service - Usage Tracking and Limit Enforcement
=====================================================
Manages usage quotas based on subscription tier.

Features:
- Check remaining quota before generation
- Track usage per user/organization
- Enforce tier-based limits
- Alert when approaching limits
"""

import logging
from datetime import date, datetime
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    User,
    Organization,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    SubscriptionTier,
    UsageRecord,
    UsageAlert,
)

logger = logging.getLogger(__name__)


# =============================================================================
# TIER LIMITS (fallback if not in DB)
# =============================================================================

DEFAULT_TIER_LIMITS = {
    SubscriptionTier.BEGINNER: {
        "monthly_rows": 10_000,           # 10K rows/month
        "rows_per_job": 1_000,            # Max 1K per generation
        "datasets_per_month": 10,         # 10 datasets
        "llm_tokens_per_month": 50_000,   # 50K LLM tokens
        "synthcity_training_gb": 0.1,     # 100MB training data
        "concurrent_jobs": 1,             # 1 concurrent job
        "features": {
            "faker": True,
            "synthcity": False,
            "llm": False,
            "api_access": False,
            "priority_queue": False,
        },
    },
    SubscriptionTier.PRO: {
        "monthly_rows": 500_000,          # 500K rows/month
        "rows_per_job": 50_000,           # Max 50K per generation
        "datasets_per_month": 100,        # 100 datasets
        "llm_tokens_per_month": 500_000,  # 500K LLM tokens
        "synthcity_training_gb": 1.0,     # 1GB training data
        "concurrent_jobs": 3,             # 3 concurrent jobs
        "features": {
            "faker": True,
            "synthcity": True,
            "llm": True,
            "api_access": True,
            "priority_queue": False,
        },
    },
    SubscriptionTier.BUSINESS: {
        "monthly_rows": 5_000_000,        # 5M rows/month
        "rows_per_job": 100_000,          # Max 100K per generation
        "datasets_per_month": 500,        # 500 datasets
        "llm_tokens_per_month": 2_000_000, # 2M LLM tokens
        "synthcity_training_gb": 10.0,    # 10GB training data
        "concurrent_jobs": 10,            # 10 concurrent jobs
        "features": {
            "faker": True,
            "synthcity": True,
            "llm": True,
            "api_access": True,
            "priority_queue": True,
            "custom_models": True,
        },
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly_rows": -1,               # Unlimited
        "rows_per_job": 100_000,          # Max per job still applies
        "datasets_per_month": -1,         # Unlimited
        "llm_tokens_per_month": -1,       # Unlimited
        "synthcity_training_gb": -1,      # Unlimited
        "concurrent_jobs": 50,            # 50 concurrent jobs
        "features": {
            "faker": True,
            "synthcity": True,
            "llm": True,
            "api_access": True,
            "priority_queue": True,
            "custom_models": True,
            "dedicated_support": True,
            "sla": True,
        },
    },
}


# =============================================================================
# QUOTA SERVICE CLASS
# =============================================================================

class QuotaService:
    """
    Service for managing usage quotas and limits.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_tier(self, user_id: UUID) -> SubscriptionTier:
        """Get user's current subscription tier."""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING,
            ]),
        ).first()
        
        if not subscription or not subscription.plan:
            return SubscriptionTier.BEGINNER
        
        return subscription.plan.tier
    
    def get_tier_limits(self, tier: SubscriptionTier) -> Dict:
        """Get limits for a subscription tier."""
        return DEFAULT_TIER_LIMITS.get(tier, DEFAULT_TIER_LIMITS[SubscriptionTier.BEGINNER])
    
    def get_current_usage(self, user_id: UUID) -> Dict:
        """Get current month's usage for a user."""
        today = date.today()
        first_of_month = today.replace(day=1)
        
        # Sum usage records for current month
        usage = self.db.query(
            func.sum(UsageRecord.data_generated_bytes).label("total_bytes"),
            func.sum(UsageRecord.datasets_created).label("total_datasets"),
            func.sum(UsageRecord.llm_tokens_used).label("total_llm_tokens"),
        ).filter(
            UsageRecord.user_id == user_id,
            UsageRecord.date >= first_of_month,
        ).first()
        
        # Estimate rows from bytes (rough: ~100 bytes per row)
        total_bytes = usage.total_bytes or 0
        estimated_rows = total_bytes // 100
        
        return {
            "rows_generated": estimated_rows,
            "bytes_generated": total_bytes,
            "datasets_created": usage.total_datasets or 0,
            "llm_tokens_used": usage.total_llm_tokens or 0,
            "period_start": first_of_month.isoformat(),
            "period_end": today.isoformat(),
        }
    
    def get_remaining_quota(self, user_id: UUID) -> Dict:
        """Get remaining quota for the current billing period."""
        tier = self.get_user_tier(user_id)
        limits = self.get_tier_limits(tier)
        usage = self.get_current_usage(user_id)
        
        def remaining(limit_key: str, usage_key: str) -> int:
            limit = limits.get(limit_key, 0)
            if limit == -1:  # Unlimited
                return -1
            used = usage.get(usage_key, 0)
            return max(0, limit - used)
        
        return {
            "tier": tier.value,
            "rows_remaining": remaining("monthly_rows", "rows_generated"),
            "datasets_remaining": remaining("datasets_per_month", "datasets_created"),
            "llm_tokens_remaining": remaining("llm_tokens_per_month", "llm_tokens_used"),
            "max_rows_per_job": limits.get("rows_per_job", 1000),
            "concurrent_jobs": limits.get("concurrent_jobs", 1),
            "features": limits.get("features", {}),
        }
    
    def check_row_quota(
        self,
        user_id: UUID,
        requested_rows: int,
    ) -> Tuple[bool, str]:
        """
        Check if user has enough row quota for a generation request.
        
        Returns:
            Tuple of (is_allowed, message)
        """
        remaining = self.get_remaining_quota(user_id)
        
        # Check per-job limit
        max_per_job = remaining.get("max_rows_per_job", 1000)
        if requested_rows > max_per_job:
            return False, f"Requested rows ({requested_rows}) exceeds per-job limit ({max_per_job})"
        
        # Check monthly quota
        rows_remaining = remaining.get("rows_remaining", 0)
        if rows_remaining != -1 and requested_rows > rows_remaining:
            return False, f"Insufficient row quota. Remaining: {rows_remaining}, Requested: {requested_rows}"
        
        return True, "OK"
    
    def check_feature_access(
        self,
        user_id: UUID,
        feature: str,
    ) -> Tuple[bool, str]:
        """
        Check if user has access to a specific feature.
        
        Features: faker, synthcity, llm, api_access, priority_queue
        """
        remaining = self.get_remaining_quota(user_id)
        features = remaining.get("features", {})
        
        if not features.get(feature, False):
            tier = remaining.get("tier", "beginner")
            return False, f"Feature '{feature}' not available on {tier} plan"
        
        return True, "OK"
    
    def record_usage(
        self,
        user_id: UUID,
        rows_generated: int = 0,
        bytes_generated: int = 0,
        datasets_created: int = 0,
        llm_tokens_used: int = 0,
        organization_id: UUID = None,
    ) -> UsageRecord:
        """Record usage for the current day."""
        today = date.today()
        
        # Get or create today's record
        record = self.db.query(UsageRecord).filter(
            UsageRecord.user_id == user_id,
            UsageRecord.date == today,
        ).first()
        
        if not record:
            record = UsageRecord(
                user_id=user_id,
                organization_id=organization_id,
                date=today,
                data_generated_bytes=0,
                datasets_created=0,
                api_calls=0,
                llm_tokens_used=0,
            )
            self.db.add(record)
        
        # Update metrics (handle potential None values)
        record.data_generated_bytes = (record.data_generated_bytes or 0) + bytes_generated
        record.datasets_created = (record.datasets_created or 0) + datasets_created
        record.llm_tokens_used = (record.llm_tokens_used or 0) + llm_tokens_used
        
        self.db.commit()
        
        # Check if we need to send alerts
        self._check_usage_alerts(user_id)
        
        return record
    
    def _check_usage_alerts(self, user_id: UUID):
        """Check and send usage alerts if thresholds are crossed."""
        remaining = self.get_remaining_quota(user_id)
        tier = self.get_user_tier(user_id)
        limits = self.get_tier_limits(tier)
        usage = self.get_current_usage(user_id)
        
        monthly_limit = limits.get("monthly_rows", 0)
        if monthly_limit == -1:
            return  # Unlimited, no alerts needed
        
        rows_used = usage.get("rows_generated", 0)
        usage_percent = (rows_used / monthly_limit) * 100 if monthly_limit > 0 else 0
        
        # Check thresholds: 80%, 95%, 100%
        thresholds = [80, 95, 100]
        
        for threshold in thresholds:
            if usage_percent >= threshold:
                # Check if alert already sent
                existing = self.db.query(UsageAlert).filter(
                    UsageAlert.user_id == user_id,
                    UsageAlert.alert_type == f"quota_{threshold}",
                    UsageAlert.created_at >= datetime.utcnow().replace(day=1),
                ).first()
                
                if not existing:
                    alert = UsageAlert(
                        user_id=user_id,
                        alert_type=f"quota_{threshold}",
                        threshold_percent=threshold,
                        message=f"You have used {usage_percent:.1f}% of your monthly row quota ({rows_used:,}/{monthly_limit:,} rows).",
                    )
                    self.db.add(alert)
                    self.db.commit()
                    
                    logger.info(f"Usage alert sent to user {user_id}: {threshold}% threshold reached")
    
    def get_usage_summary(self, user_id: UUID) -> Dict:
        """Get complete usage summary for user dashboard."""
        tier = self.get_user_tier(user_id)
        limits = self.get_tier_limits(tier)
        usage = self.get_current_usage(user_id)
        remaining = self.get_remaining_quota(user_id)
        
        monthly_rows = limits.get("monthly_rows", 0)
        rows_used = usage.get("rows_generated", 0)
        
        return {
            "tier": tier.value,
            "limits": limits,
            "usage": usage,
            "remaining": remaining,
            "usage_percent": (rows_used / monthly_rows * 100) if monthly_rows > 0 else 0,
        }


# =============================================================================
# SINGLETON / FACTORY
# =============================================================================

def get_quota_service(db: Session) -> QuotaService:
    """Get QuotaService instance for the given database session."""
    return QuotaService(db)
