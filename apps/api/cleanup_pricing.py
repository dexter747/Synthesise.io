"""
Clean up old pricing data and subscription plans from database
Run this script to remove any old data related to INR pricing
"""
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import SubscriptionPlan, Subscription, Base
from datetime import datetime

def main():
    """Clean up old pricing data"""
    print("🧹 Cleaning up old pricing data...")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Check for old subscription plans
        print("\n1️⃣ Checking for old subscription plans...")
        old_plans = db.query(SubscriptionPlan).all()
        
        if old_plans:
            print(f"   Found {len(old_plans)} existing subscription plans")
            for plan in old_plans:
                print(f"   - {plan.tier.value}: ${plan.price_monthly} monthly")
            
            # Delete old plans
            confirm = input("\n   ⚠️  Delete all existing subscription plans? (yes/no): ")
            if confirm.lower() == 'yes':
                db.query(SubscriptionPlan).delete()
                db.commit()
                print("   ✅ Deleted all old subscription plans")
            else:
                print("   ⏭️  Skipped deletion")
        else:
            print("   ℹ️  No existing subscription plans found")
        
        # 2. Check for subscriptions with old data
        print("\n2️⃣ Checking for subscriptions...")
        subscriptions = db.query(Subscription).all()
        
        if subscriptions:
            print(f"   Found {len(subscriptions)} existing subscriptions")
            
            # Update subscriptions to remove any references to old pricing
            updated_count = 0
            for subscription in subscriptions:
                if subscription.extra_data and 'inr' in str(subscription.extra_data).lower():
                    # Clean up extra_data
                    if isinstance(subscription.extra_data, dict):
                        subscription.extra_data = {
                            k: v for k, v in subscription.extra_data.items()
                            if 'inr' not in k.lower()
                        }
                        updated_count += 1
            
            if updated_count > 0:
                db.commit()
                print(f"   ✅ Cleaned up {updated_count} subscriptions with INR references")
            else:
                print("   ℹ️  No subscriptions needed cleanup")
        else:
            print("   ℹ️  No existing subscriptions found")
        
        # 3. Verify database schema changes
        print("\n3️⃣ Verifying database schema...")
        
        # Check if old columns exist using raw SQL
        inspector_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'subscription_plans' 
            AND column_name IN ('price_inr_monthly', 'price_inr_annual', 'last_login_ip')
        """)
        
        old_columns = db.execute(inspector_query).fetchall()
        
        if old_columns:
            print(f"   ⚠️  Found old columns still in database: {[col[0] for col in old_columns]}")
            print("   💡 Run migration to remove: pnpm db:migrate")
        else:
            print("   ✅ Database schema is clean (no old columns)")
        
        print("\n✨ Cleanup complete!")
        print("\n📝 Next steps:")
        print("   1. Run: pnpm db:migrate (to apply schema changes)")
        print("   2. Run: python apps/api/app/seed_data.py (to seed new pricing plans)")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
