"""add_new_transaction_fields_for_date_and_time

Revision ID: 029d3ed76890
Revises: 10b595ed3fb6
Create Date: 2025-06-05 13:15:11.860567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '029d3ed76890'
down_revision: Union[str, None] = '10b595ed3fb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('transaction_datetime_from_sms', sa.DateTime(timezone=True), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'transaction_datetime_from_sms')

