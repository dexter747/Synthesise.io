"""
Admin User Seed Script for Synthesize.io

Creates the default admin user for the admin portal.
Run with: python -m app.seed_admin
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, UserStatus, UserRole


# Admin credentials
ADMIN_EMAIL = "admin@synthesise.io"
ADMIN_PASSWORD = "Admin@1234"
ADMIN_FIRST_NAME = "Super"
ADMIN_LAST_NAME = "Admin"


def seed_admin_user(db: Session) -> None:
    """Create or update the admin user."""
    
    # Check if admin user already exists
    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    
    if existing_admin:
        print(f"Admin user '{ADMIN_EMAIL}' already exists.")
        # Update to ensure admin has correct role and status
        if existing_admin.role != UserRole.SUPER_ADMIN:
            existing_admin.role = UserRole.SUPER_ADMIN
            print(f"  → Updated role to SUPER_ADMIN")
        if existing_admin.status != UserStatus.ACTIVE:
            existing_admin.status = UserStatus.ACTIVE
            print(f"  → Updated status to ACTIVE")
        if not existing_admin.email_verified:
            existing_admin.email_verified = True
            existing_admin.email_verified_at = datetime.now(timezone.utc)
            print(f"  → Marked email as verified")
        
        # Update password
        existing_admin.password_hash = hash_password(ADMIN_PASSWORD)
        existing_admin.password_changed_at = datetime.now(timezone.utc)
        print(f"  → Password has been reset to default")
        
        db.commit()
        print(f"Admin user updated successfully!")
        return
    
    # Create new admin user
    admin_user = User(
        id=uuid.uuid4(),
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        first_name=ADMIN_FIRST_NAME,
        last_name=ADMIN_LAST_NAME,
        display_name=f"{ADMIN_FIRST_NAME} {ADMIN_LAST_NAME}",
        status=UserStatus.ACTIVE,
        role=UserRole.SUPER_ADMIN,
        email_verified=True,
        email_verified_at=datetime.now(timezone.utc),
        onboarding_completed=True,
        onboarding_step=100,
        use_case="admin",
        company_name="Synthesize.io",
        preferences={
            "theme": "dark",
            "notifications": {
                "email": True,
                "in_app": True
            },
            "dashboard": {
                "default_view": "overview"
            }
        },
        password_changed_at=datetime.now(timezone.utc),
    )
    
    db.add(admin_user)
    db.commit()
    
    print("=" * 60)
    print("ADMIN USER CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"  Email:    {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Role:     SUPER_ADMIN")
    print(f"  Status:   ACTIVE")
    print("=" * 60)
    print("")
    print("⚠️  SECURITY WARNING:")
    print("   Please change the default password immediately after first login!")
    print("=" * 60)


def run_admin_seed():
    """Run the admin seeding process."""
    print("")
    print("Starting admin user seeding...")
    print("")
    
    db = SessionLocal()
    try:
        seed_admin_user(db)
    except Exception as e:
        print(f"Error during admin seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_admin_seed()
