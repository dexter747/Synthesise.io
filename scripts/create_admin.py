#!/usr/bin/env python3
"""Create admin user script."""
import sys
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models import User
from app.core.security import hash_password
from sqlalchemy import select

def main():
    db = SessionLocal()
    admin_email = 'admin@synthesize.io'
    admin_password = 'AdminPassword123'

    try:
        existing = db.execute(select(User).where(User.email == admin_email)).scalar_one_or_none()
        if existing:
            print(f'Admin already exists: {admin_email}')
        else:
            admin = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                role='admin',
                status='active',
                email_verified=True
            )
            db.add(admin)
            db.commit()
            print(f'Created admin: {admin_email} with password: {admin_password}')
    finally:
        db.close()

if __name__ == '__main__':
    main()
