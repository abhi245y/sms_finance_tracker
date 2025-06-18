"""Add unique_hash to transactions table

Revision ID: 145aec49a5e5
Revises: ccb1a5dfa2ae
Create Date: 2025-06-10 14:49:11.935163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '145aec49a5e5'
down_revision: Union[str, None] = 'ccb1a5dfa2ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unique_hash', sa.String(length=64), nullable=False, server_default='temporary_default'))
        batch_op.alter_column('merchant_vpa',
               existing_type=sa.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=22),
               type_=sa.Enum('PENDING_ACCOUNT_SELECTION', 'PENDING_CATEGORIZATION', 'PROCESSED', 'ERROR', name='transactionstatus'),
               existing_nullable=False)

        batch_op.create_index(batch_op.f('ix_transactions_unique_hash'), ['unique_hash'], unique=True)

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('unique_hash', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_unique_hash'))
        
        batch_op.alter_column('status',
               existing_type=sa.Enum('PENDING_ACCOUNT_SELECTION', 'PENDING_CATEGORIZATION', 'PROCESSED', 'ERROR', name='transactionstatus'),
               type_=sa.VARCHAR(length=22),
               existing_nullable=False)
               
        batch_op.alter_column('merchant_vpa',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(),
               existing_nullable=True)
               
        batch_op.drop_column('unique_hash')