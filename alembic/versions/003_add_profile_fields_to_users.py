"""Add profile fields to users table

Revision ID: 003_add_profile_fields
Revises: 002_add_is_confirmed
Create Date: 2026-08-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_profile_fields"
down_revision: Union[str, None] = "002_add_is_confirmed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("mobile_number", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("address", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("profile_picture", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "profile_picture")
    op.drop_column("users", "address")
    op.drop_column("users", "bio")
    op.drop_column("users", "mobile_number")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
