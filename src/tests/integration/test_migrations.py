"""Integration tests for Alembic database migrations."""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from src.config.database import engine


@pytest.fixture(scope="module")
def alembic_config() -> Config:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "src/migrations")
    return config


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
    command.downgrade(alembic_config, "-1")
    assert _users_table_exists() is False
    command.upgrade(alembic_config, "head")
    assert _users_table_exists() is True
