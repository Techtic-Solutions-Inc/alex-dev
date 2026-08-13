"""Add ai_credit_usage column for Content Library user details."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_add_ai_credit_usage"
down_revision: str | None = "006_profile_defaults"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "ai_credit_usage",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "ai_credit_usage")
