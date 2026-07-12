"""
Webhook management endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
)
from app.services.webhook_service import WebhookService
from app.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookDetailResponse,
    WebhookDeliveryResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookEventType,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# WEBHOOK CRUD
# =============================================================================

@router.get(
    "/",
    response_model=List[WebhookResponse],
    summary="List webhooks",
)
def list_webhooks(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    include_inactive: bool = Query(False, description="Include inactive webhooks"),
):
    """List current user's webhooks."""
    webhook_service = WebhookService(db)
    webhooks, total = webhook_service.list_webhooks(
        user_id=user.id,
        include_inactive=include_inactive,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return [
        WebhookResponse(
            id=w.id,
            name=w.name,
            url=w.url,
            events=w.events or [],
            is_active=w.is_active,
            created_at=w.created_at,
            updated_at=w.updated_at,
            last_triggered_at=w.last_triggered_at,
            success_count=w.success_count or 0,
            failure_count=w.failure_count or 0,
        )
        for w in webhooks
    ]


@router.post(
    "/",
    response_model=WebhookDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create webhook",
)
def create_webhook(
    data: WebhookCreate,
    db: DBSession,
    user: CurrentUser,
):
    """Create a new webhook endpoint."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.create(
        data=data,
        user_id=user.id,
    )
    
    return WebhookDetailResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        secret_preview=webhook.secret[:8] + "..." if webhook.secret else None,
        headers=webhook.headers or {},
        retry_config=webhook.retry_config or {"max_retries": 3, "retry_delay": 60},
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
    )


# =============================================================================
# EVENT TYPES (Must be defined before /{webhook_id} routes)
# =============================================================================

@router.get(
    "/events",
    summary="List available event types",
)
def list_event_types():
    """List all available webhook event types with descriptions."""
    return {
        "events": [
            {
                "type": "generation.started",
                "description": "Triggered when a data generation job starts",
            },
            {
                "type": "generation.completed",
                "description": "Triggered when a data generation job completes successfully",
            },
            {
                "type": "generation.failed",
                "description": "Triggered when a data generation job fails",
            },
            {
                "type": "generation.progress",
                "description": "Triggered periodically with job progress updates",
            },
            {
                "type": "dataset.created",
                "description": "Triggered when a new dataset is created",
            },
            {
                "type": "dataset.updated",
                "description": "Triggered when a dataset is updated",
            },
            {
                "type": "dataset.deleted",
                "description": "Triggered when a dataset is deleted",
            },
            {
                "type": "subscription.created",
                "description": "Triggered when a new subscription is created",
            },
            {
                "type": "subscription.updated",
                "description": "Triggered when a subscription is updated",
            },
            {
                "type": "subscription.cancelled",
                "description": "Triggered when a subscription is cancelled",
            },
            {
                "type": "payment.succeeded",
                "description": "Triggered when a payment is successful",
            },
            {
                "type": "payment.failed",
                "description": "Triggered when a payment fails",
            },
            {
                "type": "usage.limit_warning",
                "description": "Triggered when usage reaches 80% of limit",
            },
            {
                "type": "usage.limit_exceeded",
                "description": "Triggered when usage limit is exceeded",
            },
        ]
    }


@router.get(
    "/{webhook_id}",
    response_model=WebhookDetailResponse,
    summary="Get webhook details",
)
def get_webhook(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get detailed information about a webhook."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.get_webhook(webhook_id, user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return WebhookDetailResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        secret_preview=webhook.secret[:8] + "..." if webhook.secret else None,
        headers=webhook.headers or {},
        retry_config=webhook.retry_config or {"max_retries": 3, "retry_delay": 60},
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        last_triggered_at=webhook.last_triggered_at,
        success_count=webhook.success_count or 0,
        failure_count=webhook.failure_count or 0,
    )


@router.put(
    "/{webhook_id}",
    response_model=WebhookResponse,
    summary="Update webhook",
)
def update_webhook(
    webhook_id: UUID,
    data: WebhookUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update webhook configuration."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.update(webhook_id, data, user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return WebhookResponse(
        id=webhook.id,
        name=webhook.name,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        success_count=webhook.success_count or 0,
        failure_count=webhook.failure_count or 0,
    )


@router.delete(
    "/{webhook_id}",
    response_model=MessageResponse,
    summary="Delete webhook",
)
def delete_webhook(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Delete a webhook."""
    webhook_service = WebhookService(db)
    success = webhook_service.delete(webhook_id, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return MessageResponse(message="Webhook deleted successfully")


# =============================================================================
# WEBHOOK ACTIONS
# =============================================================================

@router.post(
    "/{webhook_id}/enable",
    response_model=MessageResponse,
    summary="Enable webhook",
)
def enable_webhook(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Enable a disabled webhook."""
    webhook_service = WebhookService(db)
    success = webhook_service.set_active(webhook_id, user.id, True)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return MessageResponse(message="Webhook enabled")


@router.post(
    "/{webhook_id}/disable",
    response_model=MessageResponse,
    summary="Disable webhook",
)
def disable_webhook(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Disable a webhook without deleting it."""
    webhook_service = WebhookService(db)
    success = webhook_service.set_active(webhook_id, user.id, False)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return MessageResponse(message="Webhook disabled")


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    summary="Test webhook",
)
def test_webhook(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
    data: Optional[WebhookTestRequest] = None,
):
    """Send a test event to the webhook endpoint."""
    webhook_service = WebhookService(db)
    event_type = data.event_type if data else "test.ping"
    result = webhook_service.test(
        webhook_id=webhook_id,
        user_id=user.id,
        event_type=event_type,
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return WebhookTestResponse(
        success=result["success"],
        status_code=result.get("status_code"),
        response_body=result.get("response_body"),
        error_message=result.get("error_message"),
        duration_ms=result.get("duration_ms"),
    )


@router.post(
    "/{webhook_id}/rotate-secret",
    response_model=dict,
    summary="Rotate webhook secret",
)
def rotate_webhook_secret(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Generate a new signing secret for the webhook."""
    webhook_service = WebhookService(db)
    webhook = webhook_service.rotate_secret(webhook_id, user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    return {
        "secret": webhook.secret,
        "message": "New secret generated. Update your endpoint to use this secret.",
    }


# =============================================================================
# DELIVERY HISTORY
# =============================================================================

@router.get(
    "/{webhook_id}/deliveries",
    response_model=List[WebhookDeliveryResponse],
    summary="List webhook deliveries",
)
def list_deliveries(
    webhook_id: UUID,
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
):
    """List delivery attempts for a webhook."""
    webhook_service = WebhookService(db)
    
    # Verify ownership
    webhook = webhook_service.get_webhook(webhook_id, user.id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    deliveries, total = webhook_service.get_deliveries(
        webhook_id=webhook_id,
        user_id=user.id,
        page=pagination.page,
        per_page=pagination.per_page,
        status_filter=status_filter,
    )
    
    return [
        WebhookDeliveryResponse(
            id=d.id,
            webhook_id=d.webhook_id,
            event_type=d.event_type,
            payload=d.payload,
            status=d.status,
            status_code=d.status_code,
            response_body=d.response_body,
            error_message=d.error_message,
            attempt_number=d.attempt_number or 1,
            duration_ms=d.duration_ms,
            created_at=d.created_at,
            delivered_at=d.delivered_at,
        )
        for d in deliveries
    ]


@router.get(
    "/{webhook_id}/deliveries/{delivery_id}",
    response_model=WebhookDeliveryResponse,
    summary="Get delivery details",
)
def get_delivery(
    webhook_id: UUID,
    delivery_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get detailed information about a delivery attempt."""
    webhook_service = WebhookService(db)
    
    # Verify ownership
    webhook = webhook_service.get_webhook(webhook_id, user.id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    delivery = webhook_service.get_delivery(delivery_id)
    
    if not delivery or delivery.webhook_id != webhook_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        )
    
    return WebhookDeliveryResponse(
        id=delivery.id,
        webhook_id=delivery.webhook_id,
        event_type=delivery.event_type,
        payload=delivery.payload,
        status=delivery.status,
        status_code=delivery.status_code,
        response_body=delivery.response_body,
        error_message=delivery.error_message,
        attempt_number=delivery.attempt_number or 1,
        duration_ms=delivery.duration_ms,
        created_at=delivery.created_at,
        delivered_at=delivery.delivered_at,
    )


@router.post(
    "/{webhook_id}/deliveries/{delivery_id}/retry",
    response_model=MessageResponse,
    summary="Retry delivery",
)
def retry_delivery(
    webhook_id: UUID,
    delivery_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Retry a failed delivery."""
    webhook_service = WebhookService(db)
    
    # Verify ownership
    webhook = webhook_service.get_webhook(webhook_id, user.id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found",
        )
    
    success = webhook_service.retry_delivery(delivery_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot retry this delivery",
        )
    
    return MessageResponse(message="Delivery retry queued")
