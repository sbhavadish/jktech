"""fk chnage

Revision ID: 558c6f0f34c9
Revises: 2a6d5ef5de6e
Create Date: 2024-10-12 11:59:05.762816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '558c6f0f34c9'
down_revision: Union[str, None] = '2a6d5ef5de6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the current UUID-based user_id column
    op.drop_column('reviews', 'user_id')

    # Add a new user_id column with Integer type
    op.add_column('reviews', sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False))


def downgrade():
    # Drop the newly added Integer-based user_id column
    op.drop_column('reviews', 'user_id')

    # Add the old user_id column back with UUID type (in case of rollback)
    op.add_column('reviews', sa.Column('user_id', sa.UUID(), nullable=False))
