"""Add is_active column to users table.

Revision ID: 003_add_is_active
Revises: 002_add_email_verification_fields
Create Date: 2026-08-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_is_active"
down_revision: str | None = "002_email_verification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add is_active flag for account status checks."""
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    """Remove is_active flag from users."""
    op.drop_column("users", "is_active")
