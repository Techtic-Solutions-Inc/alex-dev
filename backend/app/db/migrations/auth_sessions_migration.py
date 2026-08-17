"""Create durable server-side storage for rotating refresh tokens."""

from pymongo import ASCENDING, IndexModel
from pymongo.database import Database

from app.db.migrations.base import Migration, MigrationError


class AuthSessionsMigration(Migration):
    """Add the auth session collection without mutating applied migrations."""

    revision = "0002_auth_sessions"
    description = "Create auth_sessions collection for rotating refresh tokens."

    def upgrade(self, database: Database) -> None:
        """Create refresh-session indexes idempotently."""
        database["users"].create_indexes(
            [IndexModel([("id", ASCENDING)], unique=True, name="uq_users_id")]
        )
        database["auth_sessions"].create_indexes(
            [
                IndexModel(
                    [("token_id_hash", ASCENDING)],
                    unique=True,
                    name="uq_auth_sessions_token_id_hash",
                ),
                IndexModel(
                    [("expires_at", ASCENDING)],
                    expireAfterSeconds=0,
                    name="ttl_auth_sessions_expires_at",
                ),
                IndexModel(
                    [("user_id", ASCENDING)],
                    name="ix_auth_sessions_user_id",
                ),
            ]
        )

    def downgrade(self, database: Database) -> None:
        """Remove the session collection only when doing so cannot delete data."""
        if database["auth_sessions"].find_one({}, projection={"_id": 1}) is not None:
            raise MigrationError(
                "Auth session rollback is blocked because it would delete session data."
            )
        database.drop_collection("auth_sessions")
