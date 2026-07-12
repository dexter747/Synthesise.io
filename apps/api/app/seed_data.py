"""
Seed data for Synthesize.io database.

Run with: python -m app.seed_data
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import (
    SubscriptionPlan, SubscriptionTier, SystemConfig, FeatureFlag
)


def seed_subscription_plans(db: Session) -> None:
    """Seed default subscription plans.
    
    4-tier pricing structure (NO FREE TIER):
    - Beginner: $19/month - Entry-level paid plan
    - Pro: $49/month - For individual developers (no team features)
    - Business: $299/month - For teams and organizations  
    - Enterprise: Custom - Talk to us (requires contact form)
    """
    
    # Check if plans already exist
    existing = db.query(SubscriptionPlan).first()
    if existing:
        print("Subscription plans already exist, skipping...")
        return
    
    plans = [
        # =========================
        # BEGINNER TIER - $19/month
        # =========================
        SubscriptionPlan(
            id=uuid.uuid4(),
            tier=SubscriptionTier.BEGINNER,
            name="Beginner",
            description="Perfect for getting started with synthetic data",
            monthly_price_cents=1900,  # $19
            annual_price_cents=18240,  # $182.40 (20% off)
            currency="USD",
            monthly_data_limit_gb=0.5,  # ~50,000 rows
            max_datasets=10,
            max_api_keys=0,  # No API access
            max_team_members=1,  # No team features
            api_rate_limit_per_minute=0,  # No API
            retention_days=7,
            features={
                "api_access": False,
                "priority_queue": False,
                "custom_templates": False,
                "team_collaboration": False,
                "advanced_schemas": False,
                "webhook_notifications": False,
                "export_formats": ["csv", "json"],
                "support_level": "email",
                "max_rows_per_job": 5000,
                "max_rows_per_month": 50000,
            },
            is_active=True,
            is_public=True,
            sort_order=0,
            dodo_product_id="pdt_0NWWpOaPzyUbJ0qQ0aN7q",
        ),
        # =====================
        # PRO TIER - $49/month
        # =====================
        SubscriptionPlan(
            id=uuid.uuid4(),
            tier=SubscriptionTier.PRO,
            name="Pro",
            description="For individual developers and small projects",
            monthly_price_cents=4900,  # $49
            annual_price_cents=47040,  # $470.40 (20% off - 2 months free)
            currency="USD",
            monthly_data_limit_gb=10,  # ~1,000,000 rows
            max_datasets=100,
            max_api_keys=5,
            max_team_members=1,  # No team features in Pro
            api_rate_limit_per_minute=60,
            retention_days=30,
            features={
                "api_access": True,
                "priority_queue": False,
                "custom_templates": True,
                "team_collaboration": False,  # No team in Pro
                "advanced_schemas": True,
                "webhook_notifications": False,
                "export_formats": ["csv", "json", "jsonl", "sql"],
                "support_level": "email",
                "max_rows_per_job": 100000,
                "max_rows_per_month": 1000000,
            },
            is_active=True,
            is_public=True,
            sort_order=1,
            # Dodo Payments Product ID
            dodo_product_id="pdt_0NWT8Nb1Zzv6dOJHrhzps",
        ),
        # ========================
        # BUSINESS TIER - $299/month
        # ========================
        SubscriptionPlan(
            id=uuid.uuid4(),
            tier=SubscriptionTier.BUSINESS,
            name="Business",
            description="For teams and organizations with production workloads",
            monthly_price_cents=29900,  # $299
            annual_price_cents=287040,  # $2,870.40 (20% off - 2 months free)
            currency="USD",
            monthly_data_limit_gb=100,  # ~10,000,000 rows
            max_datasets=-1,  # Unlimited
            max_api_keys=25,
            max_team_members=10,  # Team features enabled
            api_rate_limit_per_minute=300,
            retention_days=90,
            features={
                "api_access": True,
                "priority_queue": True,
                "custom_templates": True,
                "team_collaboration": True,  # Team features in Business+
                "advanced_schemas": True,
                "webhook_notifications": True,
                "export_formats": ["csv", "json", "jsonl", "sql", "parquet", "excel"],
                "support_level": "priority",
                "sla_guarantee": True,
                "max_rows_per_job": 1000000,
                "max_rows_per_month": 10000000,
            },
            is_active=True,
            is_public=True,
            sort_order=2,
            # Dodo Payments Product ID
            dodo_product_id="pdt_0NWT9B7XQo63GB3dbjPME",
        ),
        # ===========================
        # ENTERPRISE TIER - Talk to Us
        # ===========================
        SubscriptionPlan(
            id=uuid.uuid4(),
            tier=SubscriptionTier.ENTERPRISE,
            name="Enterprise",
            description="Custom solutions for enterprise needs - Contact us for pricing",
            monthly_price_cents=0,  # Custom pricing (Talk to Us)
            annual_price_cents=0,
            currency="USD",
            monthly_data_limit_gb=-1,  # Unlimited
            max_datasets=-1,  # Unlimited
            max_api_keys=-1,  # Unlimited
            max_team_members=-1,  # Unlimited
            api_rate_limit_per_minute=-1,  # Unlimited
            retention_days=365,
            features={
                "api_access": True,
                "priority_queue": True,
                "custom_templates": True,
                "team_collaboration": True,
                "advanced_schemas": True,
                "webhook_notifications": True,
                "export_formats": ["csv", "json", "jsonl", "sql", "parquet", "excel", "avro"],
                "support_level": "enterprise",
                "sla_guarantee": True,
                "custom_integrations": True,
                "on_premise_deployment": True,
                "custom_sla": True,
                "dedicated_support": True,
                "training_sessions": True,
                "max_rows_per_job": -1,  # Unlimited
                "max_rows_per_month": -1,  # Unlimited
            },
            is_active=True,
            is_public=True,  # Visible but requires contact form
            sort_order=3,
            # No Dodo product - requires enterprise contact
            dodo_product_id=None,
        ),
    ]
    
    for plan in plans:
        db.add(plan)
    
    db.commit()
    print(f"Created {len(plans)} subscription plans")


def seed_system_configs(db: Session) -> None:
    """Seed default system configurations."""
    
    existing = db.query(SystemConfig).first()
    if existing:
        print("System configs already exist, skipping...")
        return
    
    configs = [
        SystemConfig(
            key="app.maintenance_mode",
            value={"enabled": False, "message": ""},
            description="Enable/disable maintenance mode",
            is_secret=False,
        ),
        SystemConfig(
            key="app.max_upload_size_mb",
            value={"value": 100},
            description="Maximum upload size in MB",
            is_secret=False,
        ),
        SystemConfig(
            key="llm.default_model",
            value={"value": "claude-sonnet-4-20250514"},
            description="Default LLM model for data generation",
            is_secret=False,
        ),
        SystemConfig(
            key="llm.max_tokens",
            value={"value": 4096},
            description="Maximum tokens per LLM request",
            is_secret=False,
        ),
        SystemConfig(
            key="generation.max_rows_per_request",
            value={"free": 1000, "pro": 100000, "business": 1000000, "enterprise": -1},
            description="Maximum rows per generation request by tier",
            is_secret=False,
        ),
        SystemConfig(
            key="email.from_address",
            value={"value": "noreply@synthesize.io"},
            description="Default from email address",
            is_secret=False,
        ),
        SystemConfig(
            key="retention.cleanup_batch_size",
            value={"value": 100},
            description="Number of expired datasets to cleanup per batch",
            is_secret=False,
        ),
    ]
    
    for config in configs:
        db.add(config)
    
    db.commit()
    print(f"Created {len(configs)} system configs")


def seed_feature_flags(db: Session) -> None:
    """Seed default feature flags."""
    
    existing = db.query(FeatureFlag).first()
    if existing:
        print("Feature flags already exist, skipping...")
        return
    
    flags = [
        FeatureFlag(
            name="new_generation_ui",
            description="Enable the new generation UI experience",
            is_enabled=False,
            rollout_percentage=0,
        ),
        FeatureFlag(
            name="advanced_schemas",
            description="Enable advanced schema features",
            is_enabled=True,
            rollout_percentage=100,
        ),
        FeatureFlag(
            name="parquet_export",
            description="Enable Parquet export format",
            is_enabled=True,
            rollout_percentage=100,
            enabled_for_tiers=["business", "enterprise"],
        ),
        FeatureFlag(
            name="team_collaboration",
            description="Enable team collaboration features",
            is_enabled=True,
            rollout_percentage=100,
            enabled_for_tiers=["business", "enterprise"],
        ),
        FeatureFlag(
            name="api_v2",
            description="Enable API v2 endpoints",
            is_enabled=False,
            rollout_percentage=10,
        ),
        FeatureFlag(
            name="llm_streaming",
            description="Enable LLM response streaming",
            is_enabled=False,
            rollout_percentage=0,
        ),
    ]
    
    for flag in flags:
        db.add(flag)
    
    db.commit()
    print(f"Created {len(flags)} feature flags")


def run_seeds():
    """Run all seed functions."""
    print("Starting database seeding...")
    
    db = SessionLocal()
    try:
        seed_subscription_plans(db)
        seed_system_configs(db)
        seed_feature_flags(db)
        
        # Also seed admin user
        from app.seed_admin import seed_admin_user
        seed_admin_user(db)
        
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeds()
