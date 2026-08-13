"""Add user profile fields for Profile API."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_add_user_profile_fields"
down_revision: str | None = "c4626268a862"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "mobile_number",
            sa.String(length=50),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "users",
        sa.Column(
            "address_street",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "address_city",
            sa.String(length=100),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "address_state",
            sa.String(length=100),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "address_zip",
            sa.String(length=20),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "address_country",
            sa.String(length=100),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "time_zone",
            sa.String(length=50),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "time_zone")
    op.drop_column("users", "address_country")
    op.drop_column("users", "address_zip")
    op.drop_column("users", "address_state")
    op.drop_column("users", "address_city")
    op.drop_column("users", "address_street")
    op.drop_column("users", "bio")
    op.drop_column("users", "mobile_number")
