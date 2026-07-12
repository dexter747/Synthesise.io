"""merge_heads

Revision ID: afa49047eb6d
Revises: 19e6cb550c16, 0002_add_inr_pricing
Create Date: 2026-01-02 00:05:47.151230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afa49047eb6d'
down_revision: Union[str, None] = ('19e6cb550c16', '0002_add_inr_pricing')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
