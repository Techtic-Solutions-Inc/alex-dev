"""Add is_confirmed column to users table

Revision ID: 002_add_is_confirmed
Revises: 001_initial
Create Date: 2026-08-04

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002_add_is_confirmed"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_confirmed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_confirmed")
