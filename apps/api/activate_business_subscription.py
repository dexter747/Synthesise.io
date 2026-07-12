#!/usr/bin/env python3
"""Manually activate Business subscription for testing"""
import sys
sys.path.insert(0, "/Users/developer/Desktop/Synthesize.io/apps/api")

from app.database import SessionLocal
from app.models import User, Subscription, SubscriptionPlan, SubscriptionStatus, BillingCycle, PaymentProvider
from datetime import datetime, timedelta
import uuid

def activate_business_subscription(email: str):
    db = SessionLocal()
    
    try:
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get Business plan
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == 'business').first()
        if not plan:
            print("❌ Business plan not found")
            return False
        
        print(f"✅ Found plan: {plan.name} (Tier: {plan.tier})")
        
        # Cancel existing active subscriptions
        existing = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).all()
        
        for sub in existing:
            sub.status = SubscriptionStatus.CANCELED
            sub.cancelled_at = datetime.utcnow()
            print(f"✅ Cancelled existing subscription: {sub.id}")
        
        # Create new Business subscription
        now = datetime.utcnow()
        period_end = now + timedelta(days=30)
        
        new_sub = Subscription(
            id=uuid.uuid4(),
            user_id=user.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=BillingCycle.MONTHLY,
            current_period_start=now,
            current_period_end=period_end,
            dodo_subscription_id=f"manual_sub_{uuid.uuid4().hex[:12]}",
            dodo_customer_id=f"manual_cust_{uuid.uuid4().hex[:12]}",
            dodo_product_id="pdt_0NWT9B7XQo63GB3dbjPME",
            payment_provider=PaymentProvider.DODO,
        )
        
        db.add(new_sub)
        db.commit()
        
        print(f"\n🎉 SUCCESS! Business subscription activated!")
        print(f"   Subscription ID: {new_sub.id}")
        print(f"   Status: {new_sub.status.value}")
        print(f"   Plan: {plan.name}")
        print(f"   Billing: ${plan.price_monthly}/month")
        print(f"   Valid until: {period_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n✨ {user.email} now has access to ALL Business features:")
        print(f"   • 5,000,000 rows/month")
        print(f"   • Unlimited datasets")
        print(f"   • API access with webhooks")
        print(f"   • Team collaboration")
        print(f"   • Priority support")
        print(f"   • SSO (if configured)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = "maitreyakulkarni95@gmail.com"
    activate_business_subscription(email)
