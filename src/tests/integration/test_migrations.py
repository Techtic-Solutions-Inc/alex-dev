"""Integration tests for Alembic database migrations."""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from src.config.database import Base, engine


@pytest.fixture(scope="module")
def alembic_config() -> Config:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "src/migrations")
    return config


@pytest.fixture(scope="module", autouse=True)
def reset_database_for_migrations(alembic_config: Config):
    """Use a clean Alembic-managed schema instead of SQLAlchemy metadata tables."""
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    yield
    command.upgrade(alembic_config, "head")


def _users_table_exists() -> bool:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'users'"
            )
        )
        return result.fetchone() is not None


def test_initial_migration(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")
    assert _users_table_exists() is True


def test_migration_rollback(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    assert _users_table_exists() is False
    command.upgrade(alembic_config, "head")
    assert _users_table_exists() is True
