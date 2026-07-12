"""
Webhook service for Synthesize.io API.

Handles webhook endpoint management and delivery.
"""
import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

import httpx
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    AuthorizationError,
)
from app.core.security import generate_webhook_signature
from app.models import Webhook, WebhookDelivery
from app.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookTestRequest,
    WebhookTestResponse,
)


class WebhookService:
    """Service for webhook operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def create(
        self,
        data: WebhookCreate,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> Webhook:
        """Create a new webhook endpoint."""
        # Generate secret for signature verification
        secret = self._generate_secret()
        
        webhook = Webhook(
            user_id=user_id,
            organization_id=organization_id,
            name=data.name,
            url=str(data.url),
            description=data.description,
            events=data.events,
            headers=data.headers,
            secret=secret,
            is_active=data.is_active,
            failure_count=0,
            success_count=0,
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        
        return webhook
    
    def get_by_id(self, webhook_id: UUID) -> Optional[Webhook]:
        """Get webhook by ID."""
        result = self.db.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        return result.scalar_one_or_none()
    
    def get_by_id_or_raise(self, webhook_id: UUID) -> Webhook:
        """Get webhook by ID or raise NotFoundError."""
        webhook = self.get_by_id(webhook_id)
        if not webhook:
            raise NotFoundError("Webhook", str(webhook_id))
        return webhook
    
    def get_with_auth(
        self, webhook_id: UUID, user_id: UUID
    ) -> Webhook:
        """Get webhook with authorization check."""
        webhook = self.get_by_id_or_raise(webhook_id)
        
        if webhook.user_id != user_id:
            if webhook.organization_id:
                from app.services.organization_service import OrganizationService
                org_service = OrganizationService(self.db)
                if not org_service.is_member(webhook.organization_id, user_id):
                    raise AuthorizationError("You don't have access to this webhook")
            else:
                raise AuthorizationError("You don't have access to this webhook")
        
        return webhook
    
    def get_webhook(self, webhook_id: UUID, user_id: UUID) -> Webhook:
        """Get webhook by ID with authorization. Alias for get_with_auth."""
        return self.get_with_auth(webhook_id, user_id)
    
    def update(
        self, webhook_id: UUID, data: WebhookUpdate, user_id: UUID
    ) -> Webhook:
        """Update webhook."""
        webhook = self.get_with_auth(webhook_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "url" and value:
                value = str(value)
            setattr(webhook, field, value)
        
        self.db.commit()
        self.db.refresh(webhook)
        
        return webhook
    
    def delete(self, webhook_id: UUID, user_id: UUID) -> bool:
        """Delete webhook."""
        webhook = self.get_with_auth(webhook_id, user_id)
        self.db.delete(webhook)
        self.db.commit()
        return True
    
    def regenerate_secret(
        self, webhook_id: UUID, user_id: UUID
    ) -> Webhook:
        """Regenerate webhook secret."""
        webhook = self.get_with_auth(webhook_id, user_id)
        webhook.secret = self._generate_secret()
        self.db.commit()
        self.db.refresh(webhook)
        return webhook
    
    def rotate_secret(self, webhook_id: UUID, user_id: UUID) -> Webhook:
        """Rotate webhook secret. Alias for regenerate_secret."""
        return self.regenerate_secret(webhook_id, user_id)
    
    def set_active(self, webhook_id: UUID, user_id: UUID, is_active: bool) -> Webhook:
        """Enable or disable a webhook."""
        webhook = self.get_with_auth(webhook_id, user_id)
        webhook.is_active = is_active
        self.db.commit()
        self.db.refresh(webhook)
        return webhook
    
    # =========================================================================
    # LISTING
    # =========================================================================
    
    def list_webhooks(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20,
        include_inactive: bool = True,
    ) -> tuple[list[Webhook], int]:
        """List user's webhooks."""
        if organization_id:
            query = select(Webhook).where(Webhook.organization_id == organization_id)
            count_query = select(func.count(Webhook.id)).where(Webhook.organization_id == organization_id)
        else:
            query = select(Webhook).where(Webhook.user_id == user_id)
            count_query = select(func.count(Webhook.id)).where(Webhook.user_id == user_id)
        
        if not include_inactive:
            query = query.where(Webhook.is_active == True)
            count_query = count_query.where(Webhook.is_active == True)
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(Webhook.created_at.desc())
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        webhooks = list(result.scalars().all())
        
        return webhooks, total
    
    # =========================================================================
    # DELIVERY
    # =========================================================================
    
    def deliver(
        self,
        event_type: str,
        payload: dict[str, Any],
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
    ) -> list[WebhookDelivery]:
        """Deliver event to all matching webhooks."""
        # Find matching webhooks
        query = select(Webhook).where(
            and_(
                Webhook.is_active == True,
                Webhook.events.contains([event_type]),
            )
        )
        
        if organization_id:
            query = query.where(Webhook.organization_id == organization_id)
        elif user_id:
            query = query.where(Webhook.user_id == user_id)
        else:
            return []
        
        result = self.db.execute(query)
        webhooks = list(result.scalars().all())
        
        # Create delivery records
        deliveries = []
        for webhook in webhooks:
            delivery = self._create_delivery(
                webhook=webhook,
                event_type=event_type,
                payload=payload,
            )
            deliveries.append(delivery)
        
        # Queue deliveries asynchronously
        for delivery in deliveries:
            # In production, this would be a Celery task
            asyncio.create_task(self._execute_delivery(delivery.id))
        
        return deliveries
    
    def _create_delivery(
        self,
        webhook: Webhook,
        event_type: str,
        payload: dict[str, Any],
    ) -> WebhookDelivery:
        """Create a delivery record."""
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event_type=event_type,
            payload=payload,
            status="pending",
            attempt_count=0,
        )
        
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        
        return delivery
    
    def _execute_delivery(
        self, delivery_id: UUID, max_retries: int = 3
    ) -> None:
        """Execute webhook delivery with retries."""
        result = self.db.execute(
            select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()
        if not delivery:
            return
        
        webhook_result = self.db.execute(
            select(Webhook).where(Webhook.id == delivery.webhook_id)
        )
        webhook = webhook_result.scalar_one_or_none()
        if not webhook:
            delivery.status = "failed"
            delivery.error_message = "Webhook not found"
            self.db.commit()
            return
        
        # Prepare payload
        event_payload = {
            "event_id": str(uuid4()),
            "event_type": delivery.event_type,
            "created_at": datetime.utcnow().isoformat(),
            "data": delivery.payload,
        }
        
        payload_json = json.dumps(event_payload, default=str)
        
        # Generate signature
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = self._sign_payload(payload_json, webhook.secret, timestamp)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Event": delivery.event_type,
            "User-Agent": "Synthesize.io-Webhook/1.0",
        }
        
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Execute delivery
        delivery.attempt_count += 1
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers,
                )
            
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Truncate
            
            if 200 <= response.status_code < 300:
                delivery.status = "success"
                delivery.delivered_at = datetime.utcnow()
                webhook.success_count = (webhook.success_count or 0) + 1
                webhook.failure_count = 0  # Reset on success
            else:
                raise Exception(f"HTTP {response.status_code}")
            
        except Exception as e:
            delivery.status = "failed"
            delivery.error_message = str(e)[:500]
            webhook.failure_count = (webhook.failure_count or 0) + 1
            
            # Schedule retry if attempts remain
            if delivery.attempt_count < max_retries:
                delivery.status = "pending"
                delay = 60 * (2 ** (delivery.attempt_count - 1))  # Exponential backoff
                delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
            
            # Disable webhook if too many failures
            if webhook.failure_count >= 10:
                webhook.is_active = False
        
        webhook.last_triggered_at = datetime.utcnow()
        webhook.last_status_code = delivery.status_code
        
        self.db.commit()
    
    def get_deliveries(
        self,
        webhook_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        status_filter: str = None,
    ) -> tuple[list[WebhookDelivery], int]:
        """Get delivery history for webhook."""
        # Auth check
        self.get_with_auth(webhook_id, user_id)
        
        query = (
            select(WebhookDelivery)
            .where(WebhookDelivery.webhook_id == webhook_id)
            .order_by(WebhookDelivery.created_at.desc())
        )
        count_query = (
            select(func.count(WebhookDelivery.id))
            .where(WebhookDelivery.webhook_id == webhook_id)
        )
        
        # Apply status filter if provided
        if status_filter:
            query = query.where(WebhookDelivery.status == status_filter)
            count_query = count_query.where(WebhookDelivery.status == status_filter)
        
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.limit(per_page).offset((page - 1) * per_page)
        result = self.db.execute(query)
        deliveries = list(result.scalars().all())
        
        return deliveries, total
    
    def retry_delivery(
        self, delivery_id: UUID, user_id: UUID
    ) -> WebhookDelivery:
        """Retry a failed delivery."""
        result = self.db.execute(
            select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()
        if not delivery:
            raise NotFoundError("Delivery", str(delivery_id))
        
        # Auth check
        self.get_with_auth(delivery.webhook_id, user_id)
        
        if delivery.status == "success":
            raise ValidationError("Cannot retry successful delivery")
        
        delivery.status = "pending"
        delivery.next_retry_at = None
        self.db.commit()
        
        # Execute immediately
        self._execute_delivery(delivery.id)
        
        self.db.refresh(delivery)
        return delivery
    
    # =========================================================================
    # TESTING
    # =========================================================================
    
    def test(
        self,
        webhook_id: UUID,
        user_id: UUID,
        event_type: str = "test.ping",
    ) -> dict:
        """Test a webhook endpoint. Returns dict with test results."""
        webhook = self.get_with_auth(webhook_id, user_id)
        
        # Prepare test payload
        test_payload = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "created_at": datetime.utcnow().isoformat(),
            "data": {"test": True, "message": "This is a test webhook"},
        }
        
        payload_json = json.dumps(test_payload, default=str)
        
        # Generate signature
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = self._sign_payload(payload_json, webhook.secret, timestamp)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Event": event_type,
            "X-Webhook-Test": "true",
            "User-Agent": "Synthesize.io-Webhook/1.0",
        }
        
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Execute test
        start_time = datetime.utcnow()
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers,
                )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "duration_ms": int(elapsed),
                "response_body": response.text[:1000] if response.text else None,
            }
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "success": False,
                "duration_ms": int(elapsed),
                "error_message": str(e),
            }
    
    def test_webhook(
        self,
        webhook_id: UUID,
        user_id: UUID,
        data: WebhookTestRequest,
    ) -> WebhookTestResponse:
        """Test a webhook endpoint."""
        result = self.test(webhook_id, user_id, data.event_type)
        return WebhookTestResponse(
            success=result.get("success", False),
            status_code=result.get("status_code"),
            response_time_ms=result.get("duration_ms"),
            duration_ms=result.get("duration_ms"),
            response_body=result.get("response_body"),
            error_message=result.get("error_message"),
        )
    
    # =========================================================================
    # SIGNATURE VERIFICATION
    # =========================================================================
    
    def verify_signature(
        self,
        payload: str,
        signature: str,
        secret: str,
        timestamp: Optional[str] = None,
        max_age_seconds: int = 300,
    ) -> bool:
        """Verify webhook signature."""
        # Check timestamp if provided
        if timestamp:
            try:
                ts = int(timestamp)
                age = abs(int(datetime.utcnow().timestamp()) - ts)
                if age > max_age_seconds:
                    return False
            except ValueError:
                return False
        
        # Compute expected signature
        expected = self._sign_payload(payload, secret, timestamp or "")
        
        # Constant-time comparison
        return hmac.compare_digest(signature, expected)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _generate_secret(self) -> str:
        """Generate webhook secret."""
        import secrets
        return f"whsec_{secrets.token_urlsafe(32)}"
    
    def _sign_payload(
        self, payload: str, secret: str, timestamp: str
    ) -> str:
        """Sign webhook payload."""
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={signature}"


# Dependency injection helper
def get_webhook_service(db: AsyncSession) -> WebhookService:
    """Get webhook service instance."""
    return WebhookService(db)
