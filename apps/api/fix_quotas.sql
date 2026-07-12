-- Update subscription plan features with correct quota limits
-- First convert json to jsonb, update, then back to json

UPDATE subscription_plans 
SET features = (features::jsonb || '{"max_rows_per_job": 1000000, "max_rows_per_month": 10000000}'::jsonb)::json
WHERE tier = 'business';

UPDATE subscription_plans 
SET features = (features::jsonb || '{"max_rows_per_job": 100000, "max_rows_per_month": 1000000}'::jsonb)::json
WHERE tier = 'pro';

UPDATE subscription_plans 
SET features = (features::jsonb || '{"max_rows_per_job": 5000, "max_rows_per_month": 50000}'::jsonb)::json
WHERE tier = 'beginner';

UPDATE subscription_plans 
SET features = (features::jsonb || '{"max_rows_per_job": -1, "max_rows_per_month": -1}'::jsonb)::json
WHERE tier = 'enterprise';

SELECT tier, name, features::jsonb->'max_rows_per_month' as max_rows_month, features::jsonb->'max_rows_per_job' as max_rows_job FROM subscription_plans ORDER BY tier;
