"""
Add INR pricing to subscription plans
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '0002_add_inr_pricing'
down_revision = None  # Will be set by alembic
branch_labels = None
depends_on = None

def upgrade():
    # Update subscription plans to add price_inr_monthly column
    op.add_column('subscription_plans', sa.Column('price_inr_monthly', sa.Integer(), nullable=True))
    op.add_column('subscription_plans', sa.Column('price_inr_annual', sa.Integer(), nullable=True))
    
    # Update existing plans with INR pricing (rough 1 USD = 80 INR)
    op.execute("""
        UPDATE subscription_plans
        SET price_inr_monthly = monthly_price_cents * 80 / 100,
            price_inr_annual = annual_price_cents * 80 / 100
    """)
    
    # Make columns non-nullable after setting values
    op.alter_column('subscription_plans', 'price_inr_monthly', nullable=False)
    op.alter_column('subscription_plans', 'price_inr_annual', nullable=False)

def downgrade():
    op.drop_column('subscription_plans', 'price_inr_annual')
    op.drop_column('subscription_plans', 'price_inr_monthly')
