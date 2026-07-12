"""
Seed subscription plans into the database.
Run this script once to populate the subscription_plans table.
"""
from sqlalchemy.orm import Session
from app.core.database import engine
from app.models import SubscriptionPlan, SubscriptionTier
import uuid

def seed_plans():
    with Session(engine) as db:
        # Check if plans already exist
        existing = db.query(SubscriptionPlan).first()
        if existing:
            print("Plans already exist. Skipping seed.")
            return
        
        plans = [
            SubscriptionPlan(
                id=uuid.uuid4(),
                tier=SubscriptionTier.FREE.value,
                name="Free",
                description="Perfect for getting started with synthetic data",
                monthly_price_cents=0,
                annual_price_cents=0,
                monthly_data_limit_gb=0.01,  # 10MB
                max_datasets=5,
                max_api_keys=1,
                max_team_members=1,
                api_rate_limit_per_minute=30,
                retention_days=7,
                features={
                    "api_access": False,
                    "priority_queue": False,
                    "custom_schemas": False,
                    "team_collaboration": False,
                    "export_formats": ["csv", "json"],
                    "max_rows_per_dataset": 1000,
                },
                is_active=True,
                is_public=True,
                sort_order=1,
            ),
            SubscriptionPlan(
                id=uuid.uuid4(),
                tier=SubscriptionTier.PRO.value,
                name="Pro",
                description="For professional developers and teams",
                monthly_price_cents=4900,  # $49.00
                annual_price_cents=49000,  # $490.00 (~17% discount)
                monthly_data_limit_gb=1,  # 1GB
                max_datasets=-1,  # Unlimited
                max_api_keys=10,
                max_team_members=1,
                api_rate_limit_per_minute=120,
                retention_days=30,
                features={
                    "api_access": True,
                    "priority_queue": True,
                    "custom_schemas": True,
                    "team_collaboration": False,
                    "export_formats": ["csv", "json", "parquet", "excel"],
                    "max_rows_per_dataset": 100000,
                    "webhooks": True,
                    "advanced_validation": True,
                },
                is_active=True,
                is_public=True,
                sort_order=2,
            ),
            SubscriptionPlan(
                id=uuid.uuid4(),
                tier=SubscriptionTier.BUSINESS.value,
                name="Business",
                description="For growing businesses and teams",
                monthly_price_cents=29900,  # $299.00
                annual_price_cents=299000,  # $2990.00 (~17% discount)
                monthly_data_limit_gb=10,  # 10GB
                max_datasets=-1,  # Unlimited
                max_api_keys=50,
                max_team_members=10,
                api_rate_limit_per_minute=300,
                retention_days=90,
                features={
                    "api_access": True,
                    "priority_queue": True,
                    "custom_schemas": True,
                    "team_collaboration": True,
                    "export_formats": ["csv", "json", "parquet", "excel", "sql"],
                    "max_rows_per_dataset": 1000000,
                    "webhooks": True,
                    "advanced_validation": True,
                    "audit_logs": True,
                    "sso": True,
                },
                is_active=True,
                is_public=True,
                sort_order=3,
            ),
            SubscriptionPlan(
                id=uuid.uuid4(),
                tier=SubscriptionTier.ENTERPRISE.value,
                name="Enterprise",
                description="For large organizations with custom needs",
                monthly_price_cents=99900,  # $999.00
                annual_price_cents=999000,  # $9990.00
                monthly_data_limit_gb=-1,  # Unlimited
                max_datasets=-1,  # Unlimited
                max_api_keys=-1,  # Unlimited
                max_team_members=-1,  # Unlimited
                api_rate_limit_per_minute=-1,  # Unlimited
                retention_days=-1,  # Unlimited
                features={
                    "api_access": True,
                    "priority_queue": True,
                    "custom_schemas": True,
                    "team_collaboration": True,
                    "export_formats": ["csv", "json", "parquet", "excel", "sql", "avro"],
                    "max_rows_per_dataset": -1,
                    "dedicated_support": True,
                    "sla": True,
                    "on_premise": True,
                    "webhooks": True,
                    "advanced_validation": True,
                    "audit_logs": True,
                    "sso": True,
                    "custom_integrations": True,
                },
                is_active=True,
                is_public=True,
                sort_order=4,
            ),
        ]
        
        db.add_all(plans)
        db.commit()
        print(f"✅ Successfully seeded {len(plans)} subscription plans!")
        
        for plan in plans:
            price_monthly = plan.monthly_price_cents / 100
            print(f"   - {plan.name} ({plan.tier.value}): ${price_monthly:.2f}/month")

if __name__ == "__main__":
    seed_plans()
