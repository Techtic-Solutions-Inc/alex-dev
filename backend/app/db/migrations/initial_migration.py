"""Initial MongoDB collections and indexes for the existing application schema."""

from __future__ import annotations

from collections.abc import Iterable

from pymongo import ASCENDING, IndexModel
from pymongo.database import Database
from pymongo.errors import CollectionInvalid

from app.db.migrations.base import Migration, MigrationError


class InitialMigration(Migration):
    """Create the collections and unique indexes required by the original models."""

    revision = "0001_initial_schema"
    description = "Create users, blogs, and contents collections with required indexes."

    _collections: dict[str, tuple[IndexModel, ...]] = {
        "users": (
            IndexModel([("email", ASCENDING)], unique=True, name="uq_users_email"),
            IndexModel(
                [("username", ASCENDING)], unique=True, name="uq_users_username"
            ),
        ),
        "blogs": (
            IndexModel([("title", ASCENDING)], unique=True, name="uq_blogs_title"),
            IndexModel([("slug", ASCENDING)], unique=True, name="uq_blogs_slug"),
        ),
        "contents": (
            IndexModel(
                [("caption", ASCENDING)], unique=True, name="uq_contents_caption"
            ),
        ),
    }

    def upgrade(self, database: Database) -> None:
        """Create missing collections and their idempotent indexes."""
        existing_collections = set(database.list_collection_names())
        for collection_name, indexes in self._collections.items():
            if collection_name not in existing_collections:
                try:
                    database.create_collection(collection_name)
                except CollectionInvalid:
                    # Another deploy may have created it between the list and create.
                    pass
            database[collection_name].create_indexes(list(indexes))

    def downgrade(self, database: Database) -> None:
        """Drop initial collections only when doing so cannot delete application data."""
        populated = list(self._populated_collections(database))
        if populated:
            names = ", ".join(populated)
            raise MigrationError(
                "Initial schema rollback is blocked because it would delete data in: "
                f"{names}."
            )

        existing_collections = set(database.list_collection_names())
        for collection_name in self._collections:
            if collection_name in existing_collections:
                database.drop_collection(collection_name)

    def _populated_collections(self, database: Database) -> Iterable[str]:
        for collection_name in self._collections:
            if (
                collection_name in database.list_collection_names()
                and database[collection_name].find_one({}, projection={"_id": 1})
                is not None
            ):
                yield collection_name
