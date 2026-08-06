
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture(scope='module')
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option("script_location", "src/migrations")
    return config


def test_initial_migration(alembic_config):
    command.upgrade(alembic_config, "head")
    # Verify that the initial migration has been applied
    # This can be done by checking the presence of tables or specific data
    # For example, check if a specific table exists
    from src.config.database import engine
    with engine.connect() as connection:
        result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_name='your_table_name'")
        assert result.fetchone() is not None


def test_migration_rollback(alembic_config):
    command.downgrade(alembic_config, "-1")
    # Verify that the migration has been rolled back
    # For example, check if a specific table no longer exists
    from src.config.database import engine
    with engine.connect() as connection:
        result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_name='your_table_name'")
        assert result.fetchone() is None
