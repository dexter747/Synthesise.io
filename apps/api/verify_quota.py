#!/usr/bin/env python3
"""Quick quota system verification"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models import Subscription, User, UsageRecord
from datetime import date
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://synthesize:synthesize_password@localhost:5432/synthesizedb')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

user = db.query(User).filter(User.email == 'maitreyak1806@gmail.com').first()
if user:
    print(f'User: {user.email}')
    print(f'Role: {user.role}')
    
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub and sub.plan:
        features = sub.plan.features or {}
        print(f'\nPlan: {sub.plan.name} ({sub.plan.tier})')
        print(f'Status: {sub.status}')
        print(f'\nQuota Limits:')
        print(f'  Max rows/month: {features.get("max_rows_per_month")}')
        print(f'  Max rows/job: {features.get("max_rows_per_job")}')
        print(f'  API access: {features.get("api_access")}')
        print(f'  Priority queue: {features.get("priority_queue")}')
        
        month_start = date.today().replace(day=1)
        usage = db.query(
            func.sum(UsageRecord.data_generated_bytes),
            func.sum(UsageRecord.datasets_created)
        ).filter(
            UsageRecord.user_id == user.id,
            UsageRecord.date >= month_start
        ).first()
        
        bytes_used = usage[0] or 0
        rows_used = bytes_used // 100
        print(f'\nCurrent Usage:')
        print(f'  Rows used: ~{rows_used:,}')
        print(f'  Datasets created: {usage[1] or 0}')

db.close()
