# Payment Integration Guide

## Overview
Complete payment integration with Dodo Payments and Razorpay for Synthesize.io subscription management.

## Features Implemented

### 1. Payment Gateways
- **Dodo Payments**: Primary payment processor supporting multiple currencies worldwide
- **Razorpay**: Alternative payment processor for customers in India
- Automatic currency detection based on user location

### 2. Payment Flow
```
User selects plan → Checkout page → Payment gateway → Verification → Subscription activated → Dashboard
```

### 3. Backend Endpoints

#### POST /api/v1/payments/checkout
Creates a payment session with Dodo Payments or Razorpay
- **Request**: `{ tier, billing_cycle, referral_code?, return_url }`
- **Response**: `{ checkout_url, payment_id, amount, currency }`

#### GET /api/v1/payments/callback
Handles payment callback and activates subscription
- **Query**: `{ payment_id, status, signature? }`
- **Response**: Redirects to success or failure page

#### GET /api/v1/payments/config
Returns payment gateway configuration
- **Response**: `{ dodo_public_key, razorpay_key_id }`

### 4. Database Changes

#### SubscriptionPlan Model
```python
monthly_price_cents = Column(Integer)  # USD in cents
annual_price_cents = Column(Integer)   # USD in cents
price_inr_monthly = Column(Integer)    # INR
price_inr_annual = Column(Integer)     # INR
```

#### Subscription Model
- `plan_id`: Link to selected plan
- `status`: ACTIVE, CANCELLED, EXPIRED
- `payment_provider`: DODO, RAZORPAY, MANUAL
- `external_subscription_id`: Gateway payment/order ID
- `current_period_start` & `current_period_end`: Billing cycle dates

### 5. Frontend Integration

#### Checkout Page
- Dodo Payments SDK integration
- Razorpay checkout modal integration
- Location-based payment method suggestion
- Seamless redirect flow

#### Pricing Page
- Clear pricing display
- Multiple billing cycles (monthly/yearly)
- Free plan available
- Enterprise plan with custom contact

## Setup Instructions

### 1. Environment Variables
Add to `.env` file:
```env
# Dodo Payments Configuration
DODO_API_KEY=your_dodo_api_key
DODO_WEBHOOK_SECRET=your_dodo_webhook_secret

# Razorpay Configuration (Optional)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### 2. Database Migration
Run the SQL script to add INR pricing:
```bash
docker-compose exec postgres psql -U synthesize -d synthesizedb -f /scripts/add-inr-pricing.sql
```

Or manually:
```bash
cd /Users/developer/Desktop/Synthesize.io
docker-compose exec postgres psql -U synthesize -d synthesizedb < scripts/add-inr-pricing.sql
```

### 3. Test Payment Flow

#### Dodo Payments Test Mode
- Use Dodo Payments test dashboard
- Test cards provided in Dodo documentation
- Supports multiple currencies

#### Razorpay Test Cards
```
Card: 4111 1111 1111 1111
Expiry: Any future date
CVV: Any 3 digits
```

## Post-Payment Actions
When payment is verified:
1. ✅ Subscription record created/updated
2. ✅ Plan ID assigned to user
3. ✅ Status set to ACTIVE
4. ✅ Billing cycle dates set (30 days)
5. ✅ External subscription ID stored
6. ✅ User redirected to dashboard

## Testing Checklist
- [ ] Dodo Payments checkout works
- [ ] Razorpay test payment works
- [ ] Subscription created after successful payment
- [ ] User sees updated features in dashboard
- [ ] Free plan activates immediately
- [ ] Enterprise plan opens contact form

## Known Issues & TODOs
- [ ] Webhook integration for payment status updates
- [ ] Automatic subscription renewal
- [ ] Proration for plan upgrades/downgrades
- [ ] Payment history page
- [ ] Invoice generation
- [ ] Refund handling

## File Changes Summary
```
Modified:
- apps/api/app/api/v1/endpoints/payments.py (complete rewrite)
- apps/api/app/models.py (added INR pricing columns)
- apps/web/src/app/checkout/page.tsx (real SDK integration)
- apps/web/src/app/pricing/page.tsx (Olympic layout + fixed pricing)
- apps/web/src/app/auth/callback/page.tsx (better error handling)
- packages/types/src/index.ts (updated SubscriptionPlan interface)

Created:
- apps/api/alembic/versions/add_inr_pricing.py (migration)
- scripts/add-inr-pricing.sql (manual migration script)
```
