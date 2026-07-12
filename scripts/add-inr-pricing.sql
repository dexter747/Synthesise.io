-- Add INR pricing columns if they don't exist
ALTER TABLE subscription_plans 
ADD COLUMN IF NOT EXISTS price_inr_monthly INTEGER,
ADD COLUMN IF NOT EXISTS price_inr_annual INTEGER;

-- Update existing plans with INR pricing (1 USD = 80 INR)
UPDATE subscription_plans
SET 
  price_inr_monthly = COALESCE(price_inr_monthly, CAST(monthly_price_cents * 80 / 100 AS INTEGER)),
  price_inr_annual = COALESCE(price_inr_annual, CAST(annual_price_cents * 80 / 100 AS INTEGER))
WHERE price_inr_monthly IS NULL OR price_inr_annual IS NULL;

-- Make columns non-nullable after setting values
ALTER TABLE subscription_plans 
ALTER COLUMN price_inr_monthly SET NOT NULL,
ALTER COLUMN price_inr_annual SET NOT NULL;

-- Verify the changes
SELECT 
  name, 
  tier,
  monthly_price_cents as usd_cents,
  price_inr_monthly as inr_monthly,
  annual_price_cents as usd_annual_cents,
  price_inr_annual as inr_annual
FROM subscription_plans
ORDER BY monthly_price_cents;
