"""create_initial_tables

Revision ID: 0712959a81c5
Revises: 
Create Date: 2025-06-04 16:22:07.844222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0712959a81c5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('raw_sms_content', sa.Text(), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('transaction_type', sa.String(length=50), nullable=True),
        sa.Column('account_identifier', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING_CATEGORIZATION', 'PROCESSED', 'ERROR', name='transactionstatus'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
