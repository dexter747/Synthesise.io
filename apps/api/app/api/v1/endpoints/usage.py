"""
Usage & Quota API Endpoints
============================
Provides endpoints for checking usage statistics and quota limits.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_db, CurrentUser
from app.services.usage_service import UsageService, UsageQuotaExceeded

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class UsageMetric(BaseModel):
    """Individual usage metric"""
    current: int
    limit: int
    remaining: int
    percentage: int
    name: str
    unlimited: bool = False


class UsageResponse(BaseModel):
    """Full usage summary response"""
    tier: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    rows: UsageMetric
    jobs: UsageMetric
    api_calls: UsageMetric
    storage: UsageMetric
    concurrent_jobs: UsageMetric
    alerts: List[dict] = []


class QuotaCheckRequest(BaseModel):
    """Request to check specific quota"""
    usage_type: str
    amount: int = 1


class QuotaCheckResponse(BaseModel):
    """Response from quota check"""
    allowed: bool
    current: int
    limit: int
    remaining: int
    requested: int
    would_use: int
    unlimited: bool = False


class UsageHistoryItem(BaseModel):
    """Historical usage data point"""
    month: str
    month_name: str
    rows_generated: int
    jobs_created: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/summary", response_model=UsageResponse)
async def get_usage_summary(
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Get current usage summary for the authenticated user.
    
    Returns usage statistics across all metrics with quota limits
    and percentage utilization.
    """
    service = UsageService(db)
    summary = service.get_usage_summary(current_user.id)
    
    # Get quotas for concurrent jobs
    quotas = service.get_user_quotas(current_user.id)
    current = service.get_current_usage(current_user.id)
    
    concurrent_limit = quotas.get("concurrent_jobs", 1)
    concurrent_current = current.get("concurrent_jobs", 0)
    
    return UsageResponse(
        tier=summary["tier"],
        period_start=summary.get("period_start"),
        period_end=summary.get("period_end"),
        rows=UsageMetric(
            **summary["usage"]["rows_per_month"]
        ),
        jobs=UsageMetric(
            **summary["usage"]["jobs_per_month"]
        ),
        api_calls=UsageMetric(
            **summary["usage"]["api_calls_per_month"]
        ),
        storage=UsageMetric(
            **summary["usage"]["storage_mb"]
        ),
        concurrent_jobs=UsageMetric(
            current=concurrent_current,
            limit=concurrent_limit,
            remaining=max(0, concurrent_limit - concurrent_current) if concurrent_limit != -1 else -1,
            percentage=int((concurrent_current / concurrent_limit * 100)) if concurrent_limit > 0 else 0,
            name="Concurrent Jobs",
            unlimited=concurrent_limit == -1
        ),
        alerts=summary.get("alerts", [])
    )


@router.get("/quotas")
async def get_quotas(
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Get user's quota limits based on their subscription tier.
    """
    service = UsageService(db)
    quotas = service.get_user_quotas(current_user.id)
    tier = service.get_user_tier(current_user.id)
    
    return {
        "tier": tier.value,
        "quotas": {
            "rows_per_month": {
                "limit": quotas.get("rows_per_month", 0),
                "unlimited": quotas.get("rows_per_month", 0) == -1
            },
            "storage_mb": {
                "limit": quotas.get("storage_mb", 0),
                "unlimited": quotas.get("storage_mb", 0) == -1
            },
            "api_calls_per_month": {
                "limit": quotas.get("api_calls_per_month", 0),
                "unlimited": quotas.get("api_calls_per_month", 0) == -1
            },
            "jobs_per_month": {
                "limit": quotas.get("jobs_per_month", 0),
                "unlimited": quotas.get("jobs_per_month", 0) == -1
            },
            "max_rows_per_job": {
                "limit": quotas.get("max_rows_per_job", 0),
                "unlimited": quotas.get("max_rows_per_job", 0) == -1
            },
            "concurrent_jobs": {
                "limit": quotas.get("concurrent_jobs", 1),
                "unlimited": quotas.get("concurrent_jobs", 1) == -1
            }
        }
    }


@router.post("/check", response_model=QuotaCheckResponse)
async def check_quota(
    request: QuotaCheckRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Check if a specific quota is available before performing an operation.
    
    Useful for pre-validating operations like job creation or data generation.
    """
    service = UsageService(db)
    
    try:
        result = service.check_quota(
            current_user.id,
            request.usage_type,
            request.amount,
            raise_exception=False
        )
        return QuotaCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/check/rows")
async def check_row_quota(
    row_count: int = Query(..., gt=0, description="Number of rows to generate"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Check if user has quota for generating specified number of rows.
    """
    service = UsageService(db)
    
    try:
        result = service.check_row_quota(current_user.id, row_count)
        return {
            "allowed": True,
            "row_count": row_count,
            "remaining_rows": result.get("remaining", 0),
            "unlimited": result.get("unlimited", False)
        }
    except UsageQuotaExceeded as e:
        return {
            "allowed": False,
            "row_count": row_count,
            "error": str(e),
            "limit": e.limit,
            "current": e.current,
            "usage_type": e.usage_type
        }


@router.get("/check/job")
async def check_job_quota(
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Check if user can create a new generation job.
    
    Checks both monthly job quota and concurrent job limit.
    """
    service = UsageService(db)
    
    try:
        result = service.check_job_quota(current_user.id)
        return {
            "allowed": True,
            "remaining_jobs": result.get("remaining", 0),
            "unlimited": result.get("unlimited", False)
        }
    except UsageQuotaExceeded as e:
        return {
            "allowed": False,
            "error": str(e),
            "limit": e.limit,
            "current": e.current,
            "usage_type": e.usage_type
        }


@router.get("/history", response_model=List[UsageHistoryItem])
async def get_usage_history(
    months: int = Query(6, ge=1, le=24, description="Number of months of history"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Get historical usage data for the past N months.
    """
    service = UsageService(db)
    history = service.get_usage_history(current_user.id, months)
    return [UsageHistoryItem(**item) for item in history]


@router.get("/current")
async def get_current_usage(
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Get raw current usage numbers for the billing period.
    """
    service = UsageService(db)
    return service.get_current_usage(current_user.id)


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/admin/user/{user_id}")
async def admin_get_user_usage(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = None
):
    """
    Admin endpoint to get usage for any user.
    Requires admin privileges.
    """
    from app.models import UserRole
    from uuid import UUID as PyUUID
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = UsageService(db)
    
    try:
        target_user_id = PyUUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    return {
        "user_id": user_id,
        "summary": service.get_usage_summary(target_user_id),
        "quotas": service.get_user_quotas(target_user_id),
        "current": service.get_current_usage(target_user_id),
        "history": service.get_usage_history(target_user_id, 6)
    }
