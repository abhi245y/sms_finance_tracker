"""add_new_transaction_fields_for_parser

Revision ID: 10b595ed3fb6
Revises: 0712959a81c5
Create Date: 2025-06-05 12:50:06.018933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10b595ed3fb6'
down_revision: Union[str, None] = '0712959a81c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('merchant_vpa', sa.Text(), nullable=True))
    op.add_column('transactions', sa.Column('bank_name', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'merchant_vpa')
    op.drop_column('transactions', 'bank_name')
