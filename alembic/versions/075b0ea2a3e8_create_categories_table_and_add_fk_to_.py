"""create_categories_table_and_add_fk_to_transactions

Revision ID: 075b0ea2a3e8
Revises: 029d3ed76890
Create Date: 2025-06-05 15:55:59.905897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '075b0ea2a3e8'
down_revision: Union[str, None] = '029d3ed76890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'categories' table - this is fine as it's a new table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)

    # Use batch mode for operations on the existing 'transactions' table
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_index(op.f('ix_transactions_category_id'), ['category_id'], unique=False)
        batch_op.create_foreign_key(
            "fk_transactions_category_id_categories", # Constraint name
            'categories', # Target table for the FK
            ['category_id'], # Local column(s) in 'transactions' table
            ['id'] # Remote column(s) in 'categories' table
        )
        batch_op.drop_column('category')


def downgrade() -> None:
    # Use batch mode for operations on the 'transactions' table in downgrade
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        # Add back the 'category' column
        batch_op.add_column(sa.Column('category', sa.VARCHAR(length=100), nullable=True))
        # Drop the foreign key constraint
        batch_op.drop_constraint("fk_transactions_category_id_categories", type_='foreignkey')
        # Drop the index
        batch_op.drop_index(op.f('ix_transactions_category_id'))
        # Drop the column
        batch_op.drop_column('category_id')

    # Drop the 'categories' table
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')