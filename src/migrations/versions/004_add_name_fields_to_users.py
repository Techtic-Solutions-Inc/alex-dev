"""Add first_name and last_name columns to users table.

Revision ID: 004_add_name_fields
Revises: 003_add_is_active
Create Date: 2026-08-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_add_name_fields"
down_revision: str | None = "003_add_is_active"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _users_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns("users")}


def upgrade() -> None:
    """Add profile name fields for registered users."""
    columns = _users_columns()

    if "first_name" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "first_name",
                sa.String(length=100),
                nullable=False,
                server_default="",
            ),
        )
        op.alter_column("users", "first_name", server_default=None)

    if "last_name" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "last_name",
                sa.String(length=100),
                nullable=False,
                server_default="",
            ),
        )
        op.alter_column("users", "last_name", server_default=None)


def downgrade() -> None:
    """Remove profile name fields from users."""
    columns = _users_columns()

    if "last_name" in columns:
        op.drop_column("users", "last_name")
    if "first_name" in columns:
        op.drop_column("users", "first_name")
