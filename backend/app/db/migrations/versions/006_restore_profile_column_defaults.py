"""Restore server defaults on user profile columns."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_profile_defaults"
down_revision: str | None = "005_add_user_profile_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PROFILE_TEXT_COLUMNS = (
    "mobile_number",
    "bio",
    "address_street",
    "address_city",
    "address_state",
    "address_zip",
    "address_country",
    "time_zone",
)


def upgrade() -> None:
    for column in _PROFILE_TEXT_COLUMNS:
        op.execute(
            sa.text(f'UPDATE users SET "{column}" = \'\' WHERE "{column}" IS NULL')
        )
        op.alter_column("users", column, server_default="")


def downgrade() -> None:
    for column in _PROFILE_TEXT_COLUMNS:
        op.alter_column("users", column, server_default=None)
