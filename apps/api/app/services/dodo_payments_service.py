"""
Dodo Payments Service for Synthesize.io
=======================================
Handles all payment processing through Dodo Payments API.

Features:
- Subscription checkout sessions
- Payment webhooks
- Subscription management (upgrade/downgrade/cancel)
- Payment history

Dodo Payments Documentation: https://docs.dodopayments.com
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
DODO_API_KEY = os.getenv("DODO_PAYMENTS_API_KEY", "")
DODO_WEBHOOK_SECRET = os.getenv("DODO_WEBHOOK_SECRET", "")
DODO_ENVIRONMENT = os.getenv("DODO_ENVIRONMENT", "test_mode")  # "test_mode" or "live_mode"

# API Base URLs
DODO_API_BASE = "https://test.dodopayments.com" if DODO_ENVIRONMENT == "test_mode" else "https://api.dodopayments.com"
DODO_CHECKOUT_BASE = "https://test.checkout.dodopayments.com" if DODO_ENVIRONMENT == "test_mode" else "https://checkout.dodopayments.com"


class DodoProductId(str, Enum):
    """Dodo Payments Product IDs for Synthesize.io plans"""
    BEGINNER = os.getenv("DODO_PRODUCT_BEGINNER", "pdt_0NWWpOaPzyUbJ0qQ0aN7q")
    PRO = os.getenv("DODO_PRODUCT_PRO", "pdt_0NWT8Nb1Zzv6dOJHrhzps")
    BUSINESS = os.getenv("DODO_PRODUCT_BUSINESS", "pdt_0NWT9B7XQo63GB3dbjPME")


class DodoSubscriptionStatus(str, Enum):
    """Dodo subscription statuses"""
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"
    FAILED = "failed"


class DodoWebhookEvent(str, Enum):
    """Dodo webhook event types"""
    SUBSCRIPTION_ACTIVE = "subscription.active"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_ON_HOLD = "subscription.on_hold"
    SUBSCRIPTION_FAILED = "subscription.failed"
    SUBSCRIPTION_RENEWED = "subscription.renewed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"


class DodoPaymentsError(Exception):
    """Base exception for Dodo Payments errors"""
    def __init__(self, message: str, status_code: int = None, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class DodoPaymentsService:
    """
    Service for interacting with Dodo Payments API.
    
    Handles:
    - Creating checkout sessions for subscriptions
    - Managing subscriptions (upgrade, downgrade, cancel)
    - Processing webhooks
    - Fetching payment history
    """
    
    def __init__(self):
        if not DODO_API_KEY:
            logger.warning("DODO_PAYMENTS_API_KEY not configured")
        
        self.api_key = DODO_API_KEY
        self.webhook_secret = DODO_WEBHOOK_SECRET
        self.base_url = DODO_API_BASE
        self.checkout_base = DODO_CHECKOUT_BASE
        
        # HTTP client with default headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    # =========================================================================
    # CHECKOUT SESSIONS
    # =========================================================================
    
    async def create_checkout_session(
        self,
        product_id: str,
        customer_email: str,
        customer_name: str,
        return_url: str,
        metadata: Optional[Dict[str, str]] = None,
        trial_days: int = 0,
    ) -> Dict[str, Any]:
        """
        Create a Dodo Payments checkout session for subscription.
        
        Args:
            product_id: Dodo product ID (e.g., pdt_0NWT8Nb1Zzv6dOJHrhzps)
            customer_email: Customer's email
            customer_name: Customer's name
            return_url: URL to redirect after payment
            metadata: Custom metadata (e.g., user_id)
            trial_days: Number of trial days (0 for no trial)
            
        Returns:
            {
                "session_id": "cks_...",
                "checkout_url": "https://checkout.dodopayments.com/session/..."
            }
        """
        payload = {
            "product_cart": [
                {"product_id": product_id, "quantity": 1}
            ],
            "customer": {
                "email": customer_email,
                "name": customer_name,
            },
            "return_url": return_url,
        }
        
        # Add trial period if specified
        if trial_days > 0:
            payload["subscription_data"] = {"trial_period_days": trial_days}
        
        # Add metadata if provided
        if metadata:
            payload["metadata"] = metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/checkouts",
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                error_data = response.json() if response.content else {}
                raise DodoPaymentsError(
                    f"Failed to create checkout session: {response.status_code}",
                    status_code=response.status_code,
                    details=error_data,
                )
            
            data = response.json()
            logger.info(f"Created checkout session: {data.get('session_id')}")
            return data
    
    def get_static_checkout_url(
        self,
        product_id: str,
        return_url: str,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a static checkout URL (no API call needed).
        
        Args:
            product_id: Dodo product ID
            return_url: URL to redirect after payment
            customer_email: Pre-fill customer email
            customer_name: Pre-fill customer name
            metadata: Custom metadata as query params
            
        Returns:
            Static checkout URL string
        """
        url = f"{self.checkout_base}/buy/{product_id}?quantity=1"
        url += f"&redirect_url={return_url}"
        
        if customer_email:
            url += f"&email={customer_email}&disableEmail=true"
        
        if customer_name:
            # Split name for firstName/lastName if possible
            parts = customer_name.split(" ", 1)
            url += f"&firstName={parts[0]}"
            if len(parts) > 1:
                url += f"&lastName={parts[1]}"
        
        # Add metadata as query params
        if metadata:
            for key, value in metadata.items():
                url += f"&metadata_{key}={value}"
        
        return url
    
    # =========================================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================================
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details from Dodo."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to get subscription: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json()
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Dodo subscription ID
            cancel_at_period_end: If True, subscription stays active until period end
        """
        payload = {
            "cancel_at_period_end": cancel_at_period_end,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/subscriptions/{subscription_id}",
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to cancel subscription: {response.status_code}",
                    status_code=response.status_code,
                )
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return response.json()
    
    async def change_subscription_plan(
        self,
        subscription_id: str,
        new_product_id: str,
        proration_mode: str = "prorated_immediately",
    ) -> Dict[str, Any]:
        """
        Change subscription plan (upgrade/downgrade).
        
        Args:
            subscription_id: Current subscription ID
            new_product_id: New product ID to switch to
            proration_mode: "prorated_immediately", "full_immediately", or "difference_immediately"
        """
        payload = {
            "product_id": new_product_id,
            "quantity": 1,
            "proration_billing_mode": proration_mode,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}/change-plan",
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to change plan: {response.status_code}",
                    status_code=response.status_code,
                )
            
            logger.info(f"Changed subscription plan: {subscription_id} -> {new_product_id}")
            return response.json()
    
    async def update_payment_method(
        self,
        subscription_id: str,
        return_url: str,
    ) -> Dict[str, Any]:
        """
        Update payment method for a subscription (also reactivates on_hold subscriptions).
        """
        payload = {
            "type": "new",
            "return_url": return_url,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}/update-payment-method",
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to update payment method: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json()
    
    # =========================================================================
    # CUSTOMER MANAGEMENT
    # =========================================================================
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer details from Dodo."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/customers/{customer_id}",
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to get customer: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json()
    
    async def list_customer_subscriptions(self, customer_id: str) -> List[Dict]:
        """List all subscriptions for a customer."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/subscriptions",
                params={"customer_id": customer_id},
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to list subscriptions: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json().get("items", [])
    
    # =========================================================================
    # PAYMENTS
    # =========================================================================
    
    async def list_payments(
        self,
        customer_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """List payments with optional filters."""
        params = {"limit": limit}
        if customer_id:
            params["customer_id"] = customer_id
        if subscription_id:
            params["subscription_id"] = subscription_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments",
                params=params,
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to list payments: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json().get("items", [])
    
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers,
                timeout=30.0,
            )
            
            if not response.is_success:
                raise DodoPaymentsError(
                    f"Failed to get payment: {response.status_code}",
                    status_code=response.status_code,
                )
            
            return response.json()
    
    # =========================================================================
    # WEBHOOKS
    # =========================================================================
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
        webhook_id: str,
    ) -> bool:
        """
        Verify webhook signature using Standard Webhooks spec.
        
        Headers to extract:
        - webhook-id
        - webhook-signature
        - webhook-timestamp
        """
        try:
            from standardwebhooks import Webhook
            
            wh = Webhook(self.webhook_secret)
            wh.verify(
                payload,
                {
                    "webhook-id": webhook_id,
                    "webhook-signature": signature,
                    "webhook-timestamp": timestamp,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return False
    
    def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse webhook event payload.
        
        Returns standardized event structure:
        {
            "type": "subscription.active",
            "business_id": "...",
            "timestamp": "...",
            "data": {...}
        }
        """
        return {
            "type": payload.get("type"),
            "business_id": payload.get("business_id"),
            "timestamp": payload.get("timestamp"),
            "data": payload.get("data", {}),
        }


# Singleton instance
_dodo_service: Optional[DodoPaymentsService] = None


def get_dodo_payments_service() -> DodoPaymentsService:
    """Get or create Dodo Payments service instance."""
    global _dodo_service
    if _dodo_service is None:
        _dodo_service = DodoPaymentsService()
    return _dodo_service
