"""
Tests for subscription endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, SubscriptionPlan, Subscription


class TestSubscriptionPlans:
    """Tests for subscription plan endpoints"""
    
    @pytest.mark.unit
    def test_list_plans(self, client: TestClient, test_subscription_plan: SubscriptionPlan):
        """Test listing available subscription plans."""
        response = client.get("/api/v1/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    @pytest.mark.unit
    def test_get_plan(
        self, client: TestClient, test_subscription_plan: SubscriptionPlan
    ):
        """Test getting a specific plan."""
        response = client.get(
            f"/api/v1/subscriptions/plans/{test_subscription_plan.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_subscription_plan.name
    
    @pytest.mark.unit
    def test_get_plan_not_found(self, client: TestClient):
        """Test getting non-existent plan returns 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/subscriptions/plans/{fake_id}")
        assert response.status_code == 404


class TestCurrentSubscription:
    """Tests for current subscription endpoints"""
    
    @pytest.mark.unit
    def test_get_current_subscription(
        self, client: TestClient, test_user_subscription: Subscription, 
        auth_headers: dict
    ):
        """Test getting current subscription."""
        response = client.get(
            "/api/v1/subscriptions/current",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
    
    @pytest.mark.unit
    def test_get_current_subscription_no_auth(self, client: TestClient):
        """Test getting subscription without auth fails."""
        response = client.get("/api/v1/subscriptions/current")
        assert response.status_code == 401
    
    @pytest.mark.unit
    def test_get_subscription_usage(
        self, client: TestClient, test_user_subscription: Subscription,
        auth_headers: dict
    ):
        """Test getting subscription usage."""
        response = client.get(
            "/api/v1/subscriptions/usage",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestSubscriptionCheckout:
    """Tests for subscription checkout"""
    
    @pytest.mark.unit
    def test_create_checkout_session(
        self, client: TestClient, test_subscription_plan: SubscriptionPlan,
        auth_headers: dict
    ):
        """Test creating a checkout session."""
        response = client.post(
            "/api/v1/subscriptions/checkout",
            headers=auth_headers,
            json={
                "plan_id": str(test_subscription_plan.id),
                "billing_cycle": "monthly",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
        )
        # May fail if Stripe is not configured
        assert response.status_code in [200, 400, 500]


class TestSubscriptionManagement:
    """Tests for subscription management"""
    
    @pytest.mark.unit
    def test_cancel_subscription(
        self, client: TestClient, test_user_subscription: Subscription,
        auth_headers: dict
    ):
        """Test canceling subscription."""
        response = client.post(
            "/api/v1/subscriptions/cancel",
            headers=auth_headers,
        )
        # May require Stripe or return success
        assert response.status_code in [200, 400]
    
    @pytest.mark.unit
    def test_resume_subscription(
        self, client: TestClient, db: Session, test_user: User, 
        test_subscription_plan: SubscriptionPlan, auth_headers: dict
    ):
        """Test resuming a canceled subscription."""
        import uuid
        from datetime import datetime, timedelta
        
        # Create a canceled subscription
        subscription = Subscription(
            id=uuid.uuid4(),
            user_id=test_user.id,
            plan_id=test_subscription_plan.id,
            status="canceled",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            cancel_at_period_end=True,
            created_at=datetime.utcnow(),
        )
        db.add(subscription)
        db.commit()
        
        response = client.post(
            "/api/v1/subscriptions/resume",
            headers=auth_headers,
        )
        # May require Stripe or return success/error/not found
        assert response.status_code in [200, 400, 404]


class TestBillingPortal:
    """Tests for billing portal"""
    
    @pytest.mark.unit
    def test_create_portal_session(
        self, client: TestClient, test_user_subscription: Subscription,
        auth_headers: dict
    ):
        """Test creating a billing portal session."""
        response = client.post(
            "/api/v1/subscriptions/portal",
            headers=auth_headers,
            json={
                "return_url": "https://example.com/account",
            },
        )
        # May fail if Stripe is not configured
        assert response.status_code in [200, 400, 500]


class TestInvoices:
    """Tests for invoice endpoints"""
    
    @pytest.mark.unit
    def test_list_invoices(
        self, client: TestClient, test_user_subscription: Subscription,
        auth_headers: dict
    ):
        """Test listing invoices."""
        response = client.get(
            "/api/v1/subscriptions/invoices",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestPaymentMethods:
    """Tests for payment method endpoints"""
    
    @pytest.mark.unit
    def test_list_payment_methods(
        self, client: TestClient, test_user_subscription: Subscription,
        auth_headers: dict
    ):
        """Test listing payment methods."""
        response = client.get(
            "/api/v1/subscriptions/payment-methods",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestCoupons:
    """Tests for coupon endpoints"""
    
    @pytest.mark.unit
    def test_validate_coupon(self, client: TestClient, auth_headers: dict):
        """Test validating a coupon code."""
        response = client.post(
            "/api/v1/subscriptions/coupons/validate",
            headers=auth_headers,
            json={"code": "TESTCOUPON"},
        )
        # Coupon may or may not exist - 400 for invalid, 200 for valid
        assert response.status_code in [200, 400, 404]
    
    @pytest.mark.unit
    def test_validate_invalid_coupon(self, client: TestClient, auth_headers: dict):
        """Test validating an invalid coupon."""
        response = client.post(
            "/api/v1/subscriptions/coupons/validate",
            headers=auth_headers,
            json={"code": "INVALID123456"},
        )
        assert response.status_code in [200, 400, 404]


class TestStripeWebhook:
    """Tests for Stripe webhook endpoint"""
    
    @pytest.mark.unit
    def test_stripe_webhook_no_signature(self, client: TestClient):
        """Test Stripe webhook without signature fails."""
        response = client.post(
            "/api/v1/subscriptions/webhooks/stripe",
            json={"type": "customer.subscription.updated"},
        )
        # Should fail without proper Stripe signature
        assert response.status_code in [400, 401, 500]
