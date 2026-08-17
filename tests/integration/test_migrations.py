"""Integration coverage for the MongoDB migration runner."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.db.migrations import MIGRATIONS, MigrationRunner  # noqa: E402
from app.db.migrations.base import MigrationError  # noqa: E402


@pytest.fixture
def migration_database():
    """Provide an isolated MongoDB database, never a non-test database."""
    url = os.getenv("TEST_MONGODB_URL")
    database_name = os.getenv("TEST_DB_NAME")
    if not url or not database_name:
        pytest.skip("TEST_MONGODB_URL and TEST_DB_NAME are required for MongoDB tests.")
    if not database_name.lower().startswith("test"):
        pytest.skip("TEST_DB_NAME must start with 'test' to protect non-test data.")

    client = MongoClient(url, serverSelectionTimeoutMS=5_000)
    try:
        client.admin.command("ping")
    except Exception as exc:
        client.close()
        pytest.skip(f"MongoDB integration instance is unavailable: {exc}")

    database = client[database_name]
    client.drop_database(database_name)
    try:
        yield database
    finally:
        client.drop_database(database_name)
        client.close()


def test_initial_migration_applies(migration_database) -> None:
    """The initial migration creates collections, indexes, and one ledger entry."""
    runner = MigrationRunner(migration_database, MIGRATIONS)

    assert runner.upgrade() == ["0001_initial_schema"]
    assert runner.upgrade() == []

    assert {"users", "blogs", "contents", "auth_sessions", "_migrations"} <= set(
        migration_database.list_collection_names()
    )
    assert migration_database.users.index_information()["uq_users_email"]["unique"]
    assert migration_database.users.index_information()["uq_users_username"]["unique"]
    assert migration_database.blogs.index_information()["uq_blogs_slug"]["unique"]
    assert migration_database.contents.index_information()["uq_contents_caption"]["unique"]
    assert migration_database["_migrations"].count_documents({}) == 2


def test_migration_rollback(migration_database) -> None:
    """A clean initial schema can be rolled back to base and reapplied."""
    runner = MigrationRunner(migration_database, MIGRATIONS)
    runner.upgrade()

    assert runner.downgrade() == ["0001_initial_schema"]
    assert not {"users", "blogs", "contents", "auth_sessions"} & set(
        migration_database.list_collection_names()
    )
    assert migration_database["_migrations"].count_documents({}) == 0
    assert runner.upgrade() == ["0001_initial_schema"]


def test_initial_migration_rollback_protects_data(migration_database) -> None:
    """Rollback never drops a collection that contains application documents."""
    runner = MigrationRunner(migration_database, MIGRATIONS)
    runner.upgrade()
    migration_database.users.insert_one({"email": "person@example.com"})

    with pytest.raises(MigrationError, match="would delete data"):
        runner.downgrade()

    assert migration_database["_migrations"].count_documents({}) == 1
