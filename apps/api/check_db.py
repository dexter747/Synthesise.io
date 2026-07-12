#!/usr/bin/env python3
"""Quick script to check database state"""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URL))
with engine.connect() as conn:
    # Check users
    result = conn.execute(text('SELECT COUNT(*) as count FROM users'))
    user_count = result.scalar()
    print(f'Total users in DB: {user_count}')
    
    # Check recent users
    result = conn.execute(text('SELECT email, role, status, created_at FROM users ORDER BY created_at DESC LIMIT 5'))
    print('\nRecent users:')
    for row in result:
        print(f'  - {row.email} ({row.role}, {row.status}) - {row.created_at}')
    
    # Check payments
    result = conn.execute(text('SELECT COUNT(*) as count FROM payments'))
    payment_count = result.scalar()
    print(f'\nTotal payments in DB: {payment_count}')
    
    # Check subscriptions  
    result = conn.execute(text('SELECT COUNT(*) as count FROM subscriptions'))
    sub_count = result.scalar()
    print(f'Total subscriptions in DB: {sub_count}')
    
    # Check oauth accounts
    result = conn.execute(text('SELECT COUNT(*) as count FROM oauth_accounts'))
    oauth_count = result.scalar()
    print(f'Total OAuth accounts in DB: {oauth_count}')
    
    # List all OAuth accounts
    result = conn.execute(text('SELECT user_id, provider, provider_email, created_at FROM oauth_accounts'))
    print('\nOAuth accounts:')
    for row in result:
        print(f'  - {row.provider}: {row.provider_email} (User ID: {row.user_id}) - {row.created_at}')
    
    # Check if there are any test payments
    result = conn.execute(text('SELECT * FROM payments ORDER BY created_at DESC LIMIT 3'))
    print('\nRecent payments:')
    if result.rowcount == 0:
        print('  No payments found')
    else:
        for row in result:
            print(f'  - Amount: ${row.amount/100:.2f} ({row.status}) - User: {row.user_id}')
