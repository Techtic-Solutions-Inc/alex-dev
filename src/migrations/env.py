"""Alembic environment configuration.

Alembic reads the database URL from application settings (``DATABASE_URL``)
rather than the placeholder value in ``alembic.ini``. Import all SQLAlchemy
models in ``src.api.models`` so autogenerate can detect schema changes.

Common commands:
    alembic upgrade head     Apply all pending migrations
    alembic downgrade -1     Roll back the most recent migration
    alembic downgrade base   Roll back all migrations
    alembic revision --autogenerate -m "message"  Generate a new revision
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import src.api.models  # noqa: F401
from src.config.database import Base, to_sync_database_url
from src.config.settings import get_settings

config = context.config
settings = get_settings()

placeholder_url = "postgresql+psycopg2://user:password@localhost/dbname"
configured_url = config.get_main_option("sqlalchemy.url")
if not configured_url or configured_url == placeholder_url:
    sync_database_url = to_sync_database_url(settings.database_url)
    # ConfigParser treats ``%`` as interpolation syntax; escape for Alembic.
    config.set_main_option("sqlalchemy.url", sync_database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
