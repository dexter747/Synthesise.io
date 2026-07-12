"""Remove IP tracking fields and INR pricing columns

Revision ID: remove_ip_inr_001
Revises: 
Create Date: 2026-01-17

This migration:
1. Removes all ip_address columns from tracking tables
2. Removes last_used_ip from api_keys table
3. Removes last_login_ip from users table (if exists)
4. Removes price_inr_monthly and price_inr_annual from subscription_plans
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_ip_inr_001'
down_revision = 'a45430896294'  # Previous Dodo Payments migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove IP tracking and INR pricing columns."""
    
    # =========================================================================
    # REMOVE IP ADDRESS COLUMNS FROM VARIOUS TABLES
    # =========================================================================
    
    # Remove from sessions table
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from users table (last_login_ip)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_login_ip')
    
    # Remove from dataset_downloads table
    with op.batch_alter_table('dataset_downloads', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from api_keys table (last_used_ip)
    with op.batch_alter_table('api_keys', schema=None) as batch_op:
        batch_op.drop_column('last_used_ip')
    
    # Remove from api_request_logs table
    with op.batch_alter_table('api_request_logs', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from audit_logs table
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from analytics_events table
    with op.batch_alter_table('analytics_events', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from customer_queries table
    with op.batch_alter_table('customer_queries', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # Remove from enterprise_contact_requests table
    with op.batch_alter_table('enterprise_contact_requests', schema=None) as batch_op:
        batch_op.drop_column('ip_address')
    
    # =========================================================================
    # REMOVE INR PRICING COLUMNS FROM SUBSCRIPTION_PLANS
    # =========================================================================
    
    with op.batch_alter_table('subscription_plans', schema=None) as batch_op:
        batch_op.drop_column('price_inr_monthly')
        batch_op.drop_column('price_inr_annual')


def downgrade() -> None:
    """Re-add IP tracking and INR pricing columns."""
    
    # =========================================================================
    # RE-ADD INR PRICING COLUMNS TO SUBSCRIPTION_PLANS
    # =========================================================================
    
    with op.batch_alter_table('subscription_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_inr_monthly', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('price_inr_annual', sa.Integer(), nullable=True))
    
    # =========================================================================
    # RE-ADD IP ADDRESS COLUMNS TO VARIOUS TABLES
    # =========================================================================
    
    with op.batch_alter_table('enterprise_contact_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('customer_queries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('analytics_events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('api_request_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('api_keys', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_used_ip', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('dataset_downloads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login_ip', sa.String(length=45), nullable=True))
    
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=True))
