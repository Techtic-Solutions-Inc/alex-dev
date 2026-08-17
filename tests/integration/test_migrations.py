"""Integration tests for the MongoDB migration runner."""

from pymongo.database import Database

from app.db.migrations import MIGRATIONS, MigrationRunner
from app.db.migrations.base import MigrationError


def test_migration_upgrade_records_ledger(migration_db: Database) -> None:
    runner = MigrationRunner(migration_db, MIGRATIONS)
    applied = runner.upgrade()

    assert applied == ["0001_initial_schema", "0002_auth_sessions"]
    assert migration_db["_migrations"].count_documents({}) == 2


def test_migration_upgrade_is_idempotent(migration_db: Database) -> None:
    runner = MigrationRunner(migration_db, MIGRATIONS)
    assert runner.upgrade() == ["0001_initial_schema", "0002_auth_sessions"]
    assert runner.upgrade() == []


def test_initial_migration_creates_collections(migration_db: Database) -> None:
    runner = MigrationRunner(migration_db, MIGRATIONS)
    runner.upgrade()

    collection_names = set(migration_db.list_collection_names())
    assert {"users", "blogs", "contents", "auth_sessions"}.issubset(collection_names)


def test_downgrade_to_base_removes_application_collections(migration_db: Database) -> None:
    runner = MigrationRunner(migration_db, MIGRATIONS)
    runner.upgrade()
    rolled_back = runner.downgrade()

    assert rolled_back == ["0002_auth_sessions", "0001_initial_schema"]
    collection_names = set(migration_db.list_collection_names())
    assert "users" not in collection_names
    assert "auth_sessions" not in collection_names


def test_auth_sessions_downgrade_blocked_with_data(migration_db: Database) -> None:
    runner = MigrationRunner(migration_db, MIGRATIONS)
    runner.upgrade()
    migration_db["auth_sessions"].insert_one({"token_id_hash": "abc", "user_id": "user-1"})

    try:
        runner.downgrade("0001_initial_schema")
        raise AssertionError("Expected MigrationError when session data exists.")
    except MigrationError as exc:
        assert "session data" in str(exc).lower()
