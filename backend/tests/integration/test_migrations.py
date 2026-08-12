import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATIONS_DIR = BACKEND_DIR / "app" / "db" / "migrations"
DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/backend_migration_test"
)
EXPECTED_USER_COLUMNS = {"id", "username", "email", "created_at", "updated_at"}


def _get_test_database_url() -> str:
    return os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


def _ensure_database_exists(database_url: str) -> None:
    url = make_url(database_url)
    database_name = url.database
    if not database_name:
        raise ValueError("TEST_DATABASE_URL must include a database name")

    admin_url = url.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar()
            if exists is None:
                connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        engine.dispose()


def _postgres_available(database_url: str) -> bool:
    try:
        _ensure_database_exists(database_url)
        engine = create_engine(database_url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except (OperationalError, ProgrammingError, OSError):
        return False


@pytest.fixture(scope="module")
def migration_database_url() -> str:
    url = _get_test_database_url()
    if not _postgres_available(url):
        pytest.skip("PostgreSQL is not available for migration integration tests")
    return url


@pytest.fixture(scope="module")
def alembic_config(migration_database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.set_main_option("sqlalchemy.url", migration_database_url)
    return config


@pytest.fixture(scope="module")
def migration_engine(migration_database_url: str):
    engine = create_engine(migration_database_url)
    yield engine
    engine.dispose()


def test_initial_migration_file_exists() -> None:
    """Verify the initial Alembic migration script is present."""
    migrations_dir = MIGRATIONS_DIR / "versions"
    migration_files = list(migrations_dir.glob("*.py"))
    assert len(migration_files) >= 1
    assert any("initial" in migration_file.name for migration_file in migration_files)


def test_initial_migration_applies(
    alembic_config: Config,
    migration_engine,
) -> None:
    """Apply the initial migration and verify the users table schema."""
    command.downgrade(alembic_config, "base")

    inspector = inspect(migration_engine)
    assert "users" not in inspector.get_table_names()

    command.upgrade(alembic_config, "head")

    inspector = inspect(migration_engine)
    table_names = inspector.get_table_names()
    assert "users" in table_names
    assert "alembic_version" in table_names

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    assert user_columns == EXPECTED_USER_COLUMNS

    unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("users")
    }
    assert "users_email_key" in unique_constraints
    assert "users_username_key" in unique_constraints

    pk = inspector.get_pk_constraint("users")
    assert pk["constrained_columns"] == ["id"]

    command.downgrade(alembic_config, "base")

    inspector = inspect(migration_engine)
    assert "users" not in inspector.get_table_names()
