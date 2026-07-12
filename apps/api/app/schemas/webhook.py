"""
Webhook schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, HttpUrl

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# WEBHOOK ENDPOINT SCHEMAS
# =============================================================================

class WebhookCreate(BaseSchema):
    """Create a new webhook endpoint."""
    
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    description: Optional[str] = Field(None, max_length=500)
    events: list[str] = Field(
        default=["job.completed"],
        description="Events to subscribe to"
    )
    # Available events:
    # - job.started, job.completed, job.failed
    # - dataset.created, dataset.updated, dataset.deleted
    # - subscription.created, subscription.updated, subscription.canceled
    # - payment.succeeded, payment.failed
    # - usage.threshold_reached, usage.limit_exceeded
    headers: Optional[dict[str, str]] = None  # Custom headers to include
    is_active: bool = True


class WebhookUpdate(BaseSchema):
    """Update webhook endpoint."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, max_length=500)
    events: Optional[list[str]] = None
    headers: Optional[dict[str, str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseSchema, TimestampMixin):
    """Webhook endpoint response."""
    
    id: UUID
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    name: str
    url: str
    description: Optional[str] = None
    events: list[str]
    is_active: bool
    secret: Optional[str] = None  # For verifying webhook signatures
    last_triggered_at: Optional[datetime] = None
    last_status_code: Optional[int] = None
    failure_count: int = 0
    success_count: int = 0


class WebhookListResponse(PaginatedResponse[WebhookResponse]):
    """Paginated list of webhooks."""
    pass


# =============================================================================
# WEBHOOK DELIVERY SCHEMAS
# =============================================================================

class WebhookDeliveryResponse(BaseSchema):
    """Webhook delivery attempt record."""
    
    id: UUID
    webhook_id: UUID
    event_type: str
    payload: dict[str, Any]
    status: str  # pending, success, failed
    status_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_count: int
    next_retry_at: Optional[datetime]
    created_at: datetime
    delivered_at: Optional[datetime]


class WebhookDeliveryListResponse(PaginatedResponse[WebhookDeliveryResponse]):
    """Paginated list of webhook deliveries."""
    pass


# =============================================================================
# WEBHOOK TEST SCHEMAS
# =============================================================================

class WebhookTestRequest(BaseSchema):
    """Test webhook endpoint."""
    
    event_type: str = "test.ping"
    payload: Optional[dict[str, Any]] = None


class WebhookTestResponse(BaseSchema):
    """Webhook test result."""
    
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    duration_ms: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None


# =============================================================================
# WEBHOOK EVENT SCHEMAS
# =============================================================================

class WebhookEventPayload(BaseSchema):
    """Base webhook event payload."""
    
    event_id: UUID
    event_type: str
    created_at: datetime
    data: dict[str, Any]


class JobWebhookPayload(BaseSchema):
    """Payload for job-related webhooks."""
    
    job_id: UUID
    dataset_id: UUID
    dataset_name: str
    status: str
    row_count: int
    rows_generated: int
    output_format: str
    download_url: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class DatasetWebhookPayload(BaseSchema):
    """Payload for dataset-related webhooks."""
    
    dataset_id: UUID
    dataset_name: str
    action: str  # created, updated, deleted
    schema_version: int
    row_count: int


class UsageWebhookPayload(BaseSchema):
    """Payload for usage-related webhooks."""
    
    usage_type: str  # rows, api_calls, storage
    current_usage: int
    limit: int
    percentage: float
    threshold: int  # The threshold that triggered this webhook


# =============================================================================
# WEBHOOK SIGNATURE VERIFICATION
# =============================================================================

class WebhookSignatureVerifyRequest(BaseSchema):
    """Verify webhook signature (utility for users)."""
    
    payload: str
    signature: str
    secret: str
    timestamp: Optional[str] = None


class WebhookSignatureVerifyResponse(BaseSchema):
    """Signature verification result."""
    
    valid: bool
    error: Optional[str] = None


# =============================================================================
# ADDITIONAL ENDPOINT SCHEMAS
# =============================================================================

class WebhookDetailResponse(BaseSchema):
    """Detailed webhook response."""
    
    id: UUID
    name: str
    url: str
    events: list[str] = []
    is_active: bool = True
    secret_preview: Optional[str] = None  # First 8 chars + "..."
    headers: dict = {}
    retry_config: dict = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0


class WebhookEventType(BaseSchema):
    """Webhook event type info."""
    
    type: str
    description: str

