"""Add is_active column to users table

Revision ID: 004_add_is_active
Revises: 003_add_profile_fields
Create Date: 2026-08-04

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "004_add_is_active"
down_revision: str | None = "003_add_profile_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_active")
