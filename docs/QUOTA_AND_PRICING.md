# Synthesize.io - Quota & Pricing System Documentation

> **Last Updated**: January 18, 2026  
> **Purpose**: Complete reference for the subscription, quota enforcement, and pricing system

---

## 📊 Overview

Synthesize.io uses a **4-tier subscription model** with enforced quotas at multiple levels:
- **Beginner** ($19/month) - Entry-level paid plan
- **Pro** ($49/month) - For individual developers
- **Business** ($299/month) - For teams and organizations
- **Enterprise** (Custom) - Contact sales

**Important**: There is NO free tier. All users must subscribe to a paid plan after registration.

---

## 🏗️ Architecture

### Key Components

1. **SubscriptionPlan** (`apps/api/app/models.py`) - Plan definitions with limits
2. **Subscription** (`apps/api/app/models.py`) - User-plan associations with payment tracking
3. **UsageService** (`apps/api/app/services/usage_service.py`) - Quota enforcement engine
4. **Dodo Payments** (`apps/api/app/services/dodo_payments_service.py`) - Payment provider
5. **Payment Webhooks** (`apps/api/app/api/v1/endpoints/payments.py`) - Subscription activation

### Flow Diagram

```
User Registration
       ↓
Redirect to /pricing (NO FREE ACCESS)
       ↓
Select Plan → Dodo Checkout
       ↓
Payment Success → Webhook fires
       ↓
Subscription Created + Organization tier updated
       ↓
Dashboard Access Granted (with tier-based features)
```

---

## 💰 Pricing Tiers

### Tier Comparison Table

| Feature | Beginner ($19) | Pro ($49) | Business ($299) | Enterprise |
|---------|----------------|-----------|-----------------|------------|
| **Monthly Rows** | 50,000 | 1,000,000 | 10,000,000 | Unlimited |
| **Rows per Dataset** | 5,000 | 100,000 | 1,000,000 | Unlimited |
| **Datasets** | 10 | 100 | Unlimited | Unlimited |
| **Data Retention** | 7 days | 30 days | 90 days | 365 days |
| **API Access** | ❌ | ✅ | ✅ | ✅ |
| **API Calls/Month** | 0 | 10,000 | 100,000 | Unlimited |
| **Jobs/Month** | 50 | 500 | 2,000 | Unlimited |
| **Concurrent Jobs** | 1 | 3 | 10 | Unlimited |
| **Export Formats** | CSV, JSON | All | All + SQL | All + Avro |
| **Team Members** | 1 | 1 | 10 | Unlimited |
| **Support** | Email | Priority | Dedicated | White-glove |
| **Custom Schemas** | ❌ | ✅ | ✅ | ✅ |
| **Webhooks** | ❌ | ✅ | ✅ | ✅ |
| **SSO** | ❌ | ❌ | ✅ | ✅ |
| **On-Premise** | ❌ | ❌ | ❌ | ✅ |

### Dodo Payment Product IDs

| Tier | Product ID | Checkout URL |
|------|------------|--------------|
| **Beginner** | `pdt_0NWWpOaPzyUbJ0qQ0aN7q` | `https://test.checkout.dodopayments.com/buy/pdt_0NWWpOaPzyUbJ0qQ0aN7q?quantity=1` |
| **Pro** | `pdt_0NWT8Nb1Zzv6dOJHrhzps` | `https://test.checkout.dodopayments.com/buy/pdt_0NWT8Nb1Zzv6dOJHrhzps?quantity=1` |
| **Business** | `pdt_0NWT9B7XQo63GB3dbjPME` | `https://test.checkout.dodopayments.com/buy/pdt_0NWT9B7XQo63GB3dbjPME?quantity=1` |
| **Enterprise** | N/A | Contact sales |

---

## 🗄️ Database Models

### SubscriptionPlan

```python
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(UUID, primary_key=True)
    tier = Column(Enum(SubscriptionTier))  # BEGINNER, PRO, BUSINESS, ENTERPRISE
    name = Column(String(100))
    description = Column(Text)
    
    # Pricing (USD cents)
    monthly_price_cents = Column(Integer)
    annual_price_cents = Column(Integer)
    
    # Limits
    monthly_data_limit_gb = Column(Float)  # -1 = unlimited
    max_datasets = Column(Integer)         # -1 = unlimited
    max_api_keys = Column(Integer)
    max_team_members = Column(Integer)
    api_rate_limit_per_minute = Column(Integer)
    retention_days = Column(Integer)
    
    # Feature flags (JSON)
    features = Column(JSON)
    # Example: {
    #   "api_access": true,
    #   "max_rows_per_job": 100000,
    #   "max_rows_per_month": 1000000,
    #   "export_formats": ["csv", "json", "sql"],
    #   "team_collaboration": false
    # }
    
    # Dodo Payments
    dodo_product_id = Column(String(255))
```

### Subscription

```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    plan_id = Column(UUID, ForeignKey("subscription_plans.id"))
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    
    status = Column(Enum(SubscriptionStatus))
    # ACTIVE, PAST_DUE, ON_HOLD, CANCELLED, TRIALING, PAUSED, EXPIRED, PENDING
    
    billing_cycle = Column(Enum(BillingCycle))  # MONTHLY, ANNUAL
    
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    
    # Dodo references
    dodo_subscription_id = Column(String(255))
    dodo_customer_id = Column(String(255))
    dodo_product_id = Column(String(255))
    
    # Enterprise overrides
    custom_limits = Column(JSON)  # Override plan limits for enterprise
```

### SubscriptionTier Enum

```python
class SubscriptionTier(str, PyEnum):
    BEGINNER = "beginner"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
```

---

## ⚡ Quota Enforcement

### UsageService (`apps/api/app/services/usage_service.py`)

The core quota enforcement service with Redis caching:

```python
class UsageService:
    TIER_QUOTAS = {
        SubscriptionTier.BEGINNER: {
            "rows_per_month": 50000,
            "storage_mb": 500,
            "api_calls_per_month": 0,
            "jobs_per_month": 50,
            "max_rows_per_job": 5000,
            "concurrent_jobs": 1
        },
        SubscriptionTier.PRO: {
            "rows_per_month": 1000000,
            "storage_mb": 5000,
            "api_calls_per_month": 10000,
            "jobs_per_month": 500,
            "max_rows_per_job": 100000,
            "concurrent_jobs": 3
        },
        # ... etc
    }
    
    def check_quota(self, user_id, usage_type, amount) -> bool:
        """Check if user has quota available"""
        quotas = self.get_user_quotas(user_id)
        current = self.get_current_usage(user_id)
        
        limit = quotas.get(usage_type, 0)
        if limit == -1:  # Unlimited
            return True
        
        if current.get(usage_type, 0) + amount > limit:
            raise UsageQuotaExceeded(usage_type, limit, current.get(usage_type, 0))
        
        return True
```

### FastAPI Dependencies (`apps/api/app/api/deps.py`)

```python
# Type-safe quota checking dependencies
JobQuotaUser = Annotated[User, Depends(check_job_creation_quota)]
APIQuotaUser = Annotated[User, Depends(check_api_call_quota)]

# Usage in endpoints
@router.post("/generate")
async def create_generation(
    user: JobQuotaUser,  # Automatically checks quota
):
    ...
```

### HTTP Response on Quota Exceeded

```json
{
  "status_code": 429,
  "detail": {
    "message": "Quota exceeded for rows_per_month",
    "usage_type": "rows_per_month",
    "limit": 50000,
    "current": 48500,
    "upgrade_url": "/pricing"
  }
}
```

---

## 💳 Payment Flow

### 1. Checkout Creation

```
POST /api/v1/payments/checkout
{
  "tier": "pro",
  "billing_cycle": "monthly",
  "return_url": "https://app.synthesize.io/payment/callback?plan=xxx"
}
```

### 2. Dodo Redirect

User redirected to Dodo checkout page with:
- Product ID from plan
- User metadata (user_id, email, tier)
- Return URL for callback

### 3. Webhook Processing

Dodo fires webhook to `/api/v1/payments/webhooks/dodo`:

```python
# Key events handled:
"subscription.active"     # Create subscription, update org tier
"subscription.on_hold"    # Payment failed (grace period)
"subscription.renewed"    # Extend period
"subscription.cancelled"  # Mark cancelled
"payment.succeeded"       # Record payment
"payment.failed"          # Log failure
```

### 4. Subscription Activation

```python
# In webhook handler (payments.py):
def process_subscription_active(db, event_data):
    # Create subscription record
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        dodo_subscription_id=dodo_sub_id,
        current_period_end=period_end,
    )
    db.add(subscription)
    
    # CRITICAL: Update organization tier for quota enforcement
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.primary_organization_id:
        org = db.query(Organization).filter(
            Organization.id == user.primary_organization_id
        ).first()
        if org:
            org.subscription_tier = tier
    
    db.commit()
```

---

## 🚪 Access Control

### No Free Access Policy

After registration, users MUST subscribe before accessing dashboard:

```typescript
// auth-provider.tsx
useEffect(() => {
  if (user && !user.subscription_tier) {
    router.push('/pricing');  // Force to pricing page
  }
}, [user]);
```

### Dashboard Access Check

```typescript
// Protected routes check subscription status
if (!user.subscription_tier || user.subscription_status === 'expired') {
  return <SubscriptionRequired />;
}
```

### Feature Visibility by Tier

```typescript
// Components check user tier for feature access
const canUseAPI = ['pro', 'business', 'enterprise'].includes(user.subscription_tier);
const canUseTeams = ['business', 'enterprise'].includes(user.subscription_tier);
const canUseWebhooks = ['pro', 'business', 'enterprise'].includes(user.subscription_tier);
```

---

## ⏰ Subscription Expiry

### Expiry Handling

1. **Grace Period**: 7 days after payment failure (ON_HOLD status)
2. **Feature Restriction**: During grace period, read-only access
3. **Full Expiry**: After grace period, redirect to pricing

### Celery Task for Expiry Check

```python
# apps/api/app/tasks/cleanup.py
@celery_app.task
def check_subscription_expiry():
    """Run daily to check and expire subscriptions"""
    expired = db.query(Subscription).filter(
        Subscription.current_period_end < datetime.utcnow(),
        Subscription.status == SubscriptionStatus.ON_HOLD
    ).all()
    
    for sub in expired:
        if sub.current_period_end < datetime.utcnow() - timedelta(days=GRACE_PERIOD_DAYS):
            sub.status = SubscriptionStatus.EXPIRED
            # Notify user
    
    db.commit()
```

---

## 👨‍💼 Admin Panel Management

### User Subscription Management

Admin can:
1. **View subscription details** - Plan, status, period dates
2. **Manually change plan** - Upgrade/downgrade user tier
3. **Override quotas** - Set custom limits for specific users
4. **Extend subscription** - Add days to period
5. **Cancel subscription** - Immediately or at period end
6. **Apply credits** - Add usage credits

### Admin API Endpoints

```
GET  /admin/subscriptions              # List all subscriptions
GET  /admin/subscriptions/:id          # Get subscription details
PUT  /admin/subscriptions/:id/plan     # Change plan
PUT  /admin/subscriptions/:id/status   # Change status
PUT  /admin/subscriptions/:id/extend   # Extend period
PUT  /admin/subscriptions/:id/limits   # Set custom limits
POST /admin/subscriptions/:id/credit   # Apply credits

GET  /admin/users/:id/usage            # Get user usage stats
PUT  /admin/users/:id/quota-override   # Override quotas
```

### Quota Override Format

```json
{
  "custom_limits": {
    "rows_per_month": 200000,
    "max_rows_per_job": 50000,
    "concurrent_jobs": 5
  },
  "reason": "Customer dispute resolution",
  "expires_at": "2026-02-18T00:00:00Z"
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Dodo Payments
DODO_PAYMENTS_API_KEY=sk_test_xxx
DODO_PAYMENTS_WEBHOOK_SECRET=whsec_xxx
DODO_PAYMENTS_TEST_MODE=true

# Subscription Settings
GRACE_PERIOD_DAYS=7
MAX_RETRY_ATTEMPTS=3

# Redis (for quota caching)
REDIS_URL=redis://localhost:6379/0
```

### Webhook Configuration

Configure in Dodo Dashboard:
```
Production: https://api.synthesize.io/api/v1/payments/webhooks/dodo
Development: Use ngrok or test activation endpoint
```

**Note**: Localhost webhooks do NOT work. Use ngrok for development:
```bash
ngrok http 8000
# Then configure: https://{ngrok-id}.ngrok.io/api/v1/payments/webhooks/dodo
```

---

## 🧪 Testing

### Test Activation Endpoint (Development Only)

```
POST /api/v1/payments/test/activate-subscription
{
  "tier": "pro"
}
```

This bypasses payment for development testing.

### Test Scenarios

1. **New user flow**: Register → Pricing → Checkout → Dashboard
2. **Quota enforcement**: Generate data until limit reached
3. **Plan upgrade**: Upgrade from Beginner to Pro
4. **Expiry handling**: Simulate expired subscription
5. **Admin override**: Apply custom quota limits

---

## 📝 Migration Notes

### From Free to Beginner Tier

1. Update `SubscriptionTier` enum (add BEGINNER)
2. Update seed data with Beginner plan
3. Update all "free" references to "beginner"
4. Update pricing display components
5. Add payment requirement before dashboard access
6. Run migration to update existing FREE users (if any)

### SQL Migration

```sql
-- Add BEGINNER to tier enum
ALTER TYPE subscriptiontier ADD VALUE 'beginner';

-- Update existing free tier to beginner
UPDATE subscription_plans 
SET tier = 'beginner', 
    name = 'Beginner',
    monthly_price_cents = 1900,
    dodo_product_id = 'pdt_0NWWpOaPzyUbJ0qQ0aN7q'
WHERE tier = 'free';
```

---

## 🚀 Quick Reference

### Check User's Tier
```python
tier = usage_service.get_user_tier(user_id)
```

### Check Quota Before Action
```python
usage_service.check_quota(user_id, "rows_per_month", row_count)
```

### Get Usage Summary
```python
summary = usage_service.get_usage_summary(user_id)
# Returns: tier, usage, limits, alerts
```

### Create Subscription (Manual)
```python
from app.services.subscription_service import create_subscription
subscription = create_subscription(db, user_id, plan_id, billing_cycle)
```

---

*This document is the source of truth for the Synthesize.io quota and pricing system.*
