"""rename_free_tier_to_beginner

Revision ID: 1e11615ac8fe
Revises: remove_ip_inr_001
Create Date: 2026-01-18 09:26:17.101462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e11615ac8fe'
down_revision: Union[str, None] = 'remove_ip_inr_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # For PostgreSQL enums, we need to use a workaround
    # We'll add 'beginner', update records, but keep 'free' in the enum
    
    # Get connection
    connection = op.get_bind()
    
    # Step 1: Add 'beginner' to the enum using raw connection (outside transaction)
    connection.execute(sa.text("COMMIT"))  # Commit current transaction
    connection.execute(sa.text("ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'beginner'"))
    connection.execute(sa.text("BEGIN"))  # Start new transaction
    
    # Step 2: Update subscription_plans tier from 'free' to 'beginner'
    # This is the only table with a direct tier column
    connection.execute(sa.text("""
        UPDATE subscription_plans 
        SET tier = 'beginner' 
        WHERE tier = 'free'
    """))


def downgrade() -> None:
    # Downgrade: change 'beginner' back to 'free'
    connection = op.get_bind()
    
    connection.execute(sa.text("""
        UPDATE subscription_plans 
        SET tier = 'free' 
        WHERE tier = 'beginner'
    """))

