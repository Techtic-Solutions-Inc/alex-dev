"""Add account_status to users table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

account_status_enum = sa.Enum('active', 'inactive', 'suspended', name='accountstatus')


def upgrade() -> None:
    account_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'users',
        sa.Column(
            'account_status',
            account_status_enum,
            nullable=False,
            server_default='active',
        ),
    )


def downgrade() -> None:
    op.drop_column('users', 'account_status')
    account_status_enum.drop(op.get_bind(), checkfirst=True)
