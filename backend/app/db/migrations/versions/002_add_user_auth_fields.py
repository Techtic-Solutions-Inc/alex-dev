"""Add user auth fields — first_name, last_name, hashed_password, is_locked."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_user_auth_fields"
down_revision: str | None = "001_initial_migration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("first_name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "users",
        sa.Column("last_name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "first_name", server_default=None)
    op.alter_column("users", "last_name", server_default=None)
    op.alter_column("users", "hashed_password", server_default=None)
    op.alter_column("users", "is_locked", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_locked")
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
