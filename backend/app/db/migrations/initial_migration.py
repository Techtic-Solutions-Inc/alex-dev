from pymongo import ASCENDING, IndexModel
from app.db.migrations.base import Migration

class InitialMigration(Migration):
    revision = "0001_initial_schema"
    description = "Create core collections and indexes."

    def upgrade(self, database):
        # Create collections
        database.create_collection("users")
        database.create_collection("blogs")
        database.create_collection("contents")
        database.create_collection("auth_sessions")

        # Create indexes
        database["users"].create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="uq_users_email"),
            IndexModel([("username", ASCENDING)], unique=True, name="uq_users_username")
        ])
        database["blogs"].create_indexes([
            IndexModel([("slug", ASCENDING)], unique=True, name="uq_blogs_slug")
        ])
        database["contents"].create_indexes([
            IndexModel([("caption", ASCENDING)], unique=True, name="uq_contents_caption")
        ])

    def downgrade(self, database):
        # Drop indexes
        database["users"].drop_index("uq_users_email")
        database["users"].drop_index("uq_users_username")
        database["blogs"].drop_index("uq_blogs_slug")
        database["contents"].drop_index("uq_contents_caption")

        # Drop collections
        database.drop_collection("users")
        database.drop_collection("blogs")
        database.drop_collection("contents")
        database.drop_collection("auth_sessions")
