"""Add password reset token fields to users table.

Revision ID: 005_password_reset
Revises: 004_add_name_fields
Create Date: 2026-08-07 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_password_reset"
down_revision: str | None = "004_add_name_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _users_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns("users")}


def upgrade() -> None:
    """Add password reset token columns to the users table."""
    columns = _users_columns()

    if "password_reset_token" not in columns:
        op.add_column(
            "users",
            sa.Column("password_reset_token", sa.String(length=255), nullable=True),
        )
    if "password_reset_token_expires_at" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "password_reset_token_expires_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("users")
    }
    if "uq_users_password_reset_token" not in unique_constraints:
        op.create_unique_constraint(
            "uq_users_password_reset_token",
            "users",
            ["password_reset_token"],
        )


def downgrade() -> None:
    """Remove password reset token columns from the users table."""
    columns = _users_columns()

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("users")
    }
    if "uq_users_password_reset_token" in unique_constraints:
        op.drop_constraint("uq_users_password_reset_token", "users", type_="unique")

    if "password_reset_token_expires_at" in columns:
        op.drop_column("users", "password_reset_token_expires_at")
    if "password_reset_token" in columns:
        op.drop_column("users", "password_reset_token")
