"""
Simple cleanup script using raw SQL to remove old pricing data
"""
import psycopg2
from psycopg2 import sql
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://synthesize:synthesize_password@localhost:5432/synthesizedb')

def main():
    """Clean up old pricing data using raw SQL"""
    print("🧹 Cleaning up old pricing and subscription data...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # 1. Delete all existing subscriptions (they'll be recreated with proper data)
        print("\n1️⃣ Deleting existing subscriptions...")
        cur.execute("SELECT COUNT(*) FROM subscriptions")
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"   Found {count} subscriptions")
            confirm = input("   ⚠️  Delete all subscriptions? (yes/no): ")
            if confirm.lower() == 'yes':
                cur.execute("DELETE FROM subscriptions")
                print(f"   ✅ Deleted {count} subscriptions")
            else:
                print("   ⏭️  Skipped")
        else:
            print("   ℹ️  No subscriptions found")
        
        # 2. Delete all existing subscription plans
        print("\n2️⃣ Deleting existing subscription plans...")
        cur.execute("SELECT COUNT(*) FROM subscription_plans")
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"   Found {count} subscription plans")
            confirm = input("   ⚠️  Delete all subscription plans? (yes/no): ")
            if confirm.lower() == 'yes':
                cur.execute("DELETE FROM subscription_plans")
                print(f"   ✅ Deleted {count} subscription plans")
            else:
                print("   ⏭️  Skipped")
        else:
            print("   ℹ️  No subscription plans found")
        
        # 3. Delete old payments if any
        print("\n3️⃣ Cleaning up payments...")
        cur.execute("SELECT COUNT(*) FROM payments")
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"   Found {count} payments")
            confirm = input("   ⚠️  Delete all payments? (yes/no): ")
            if confirm.lower() == 'yes':
                cur.execute("DELETE FROM payments")
                print(f"   ✅ Deleted {count} payments")
            else:
                print("   ⏭️  Skipped")
        else:
            print("   ℹ️  No payments found")
        
        conn.commit()
        
        print("\n✨ Database cleanup complete!")
        print("\n📝 Next steps:")
        print("   1. Run: cd apps/api && source venv/bin/activate && alembic upgrade head")
        print("   2. Run: python apps/api/app/seed_data.py")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
