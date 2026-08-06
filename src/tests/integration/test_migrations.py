"""Integration tests for Alembic database migrations."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _build_alembic_config(database_url: str) -> Config:
    """Return an Alembic config bound to the supplied database URL."""
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    return alembic_cfg


def _database_is_available(database_url: str) -> bool:
    """Return True when the database accepts connections."""
    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    try:
        test_engine = create_engine(database_url, connect_args=connect_args)
        with test_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False


@pytest.fixture(scope="module")
def migration_database_url() -> str:
    """Use an isolated SQLite database for migration tests when possible."""
    sqlite_path = PROJECT_ROOT / "migration_test.db"
    if sqlite_path.exists():
        sqlite_path.unlink()
    return f"sqlite:///{sqlite_path}"


@pytest.fixture(scope="module")
def alembic_config(migration_database_url: str) -> Config:
    """Provide Alembic configuration for migration tests."""
    return _build_alembic_config(migration_database_url)


@pytest.fixture(autouse=True)
def clean_migration_state(migration_database_url: str, alembic_config: Config) -> None:
    """Ensure each test starts from a clean migration state."""
    if not _database_is_available(migration_database_url):
        pytest.skip("Migration test database is not available.")
    command.downgrade(alembic_config, "base")


def _get_inspector(database_url: str):
    """Return a SQLAlchemy inspector for the given database URL."""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )
    return inspect(engine)


def test_initial_migration_applied(
    alembic_config: Config, migration_database_url: str
) -> None:
    """Initial migration should create the users table and Alembic version table."""
    command.upgrade(alembic_config, "head")

    inspector = _get_inspector(migration_database_url)

    assert "users" in inspector.get_table_names()

    column_names = {column["name"] for column in inspector.get_columns("users")}
    assert column_names == {
        "id",
        "username",
        "email",
        "password_hash",
        "created_at",
        "updated_at",
    }

    unique_constraints = {
        constraint["name"] for constraint in inspector.get_unique_constraints("users")
    }
    assert "uq_users_email" in unique_constraints
    assert "uq_users_username" in unique_constraints

    with create_engine(
        migration_database_url,
        connect_args={"check_same_thread": False},
    ).connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        version_row = result.fetchone()
        assert version_row is not None
        assert version_row[0] == "001_initial"


def test_migration_rollback(
    alembic_config: Config, migration_database_url: str
) -> None:
    """Rolling back the initial migration should remove application tables."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    inspector = _get_inspector(migration_database_url)

    assert "users" not in inspector.get_table_names()

    with create_engine(
        migration_database_url,
        connect_args={"check_same_thread": False},
    ).connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        assert result.fetchone() is None


def test_migration_downgrade_one_step(
    alembic_config: Config, migration_database_url: str
) -> None:
    """Rolling back one step should remove the users table while at base revision."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "-1")

    inspector = _get_inspector(migration_database_url)

    assert "users" not in inspector.get_table_names()

    with create_engine(
        migration_database_url,
        connect_args={"check_same_thread": False},
    ).connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        assert result.fetchone() is None
