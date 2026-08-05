import asyncio
import logging
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

from models import Base

load_dotenv(project_root / ".env")
load_dotenv(project_root / "src" / ".env")
load_dotenv(project_root / ".env.test", override=False)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

log = logging.getLogger("alembic.env")


def _normalize_database_url(url: str | None) -> str | None:
    """Ensure Alembic receives an async PostgreSQL driver URL."""
    if not url:
        return None
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


database_url = _normalize_database_url(
    os.getenv("DATABASE_URL") or os.getenv("DB_URL")
)
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    log.warning(
        "DATABASE_URL is not set. Falling back to sqlalchemy.url in alembic.ini. "
        "Set DATABASE_URL or DB_URL in your environment or .env file."
    )


def include_name(
    name: str | None, type_: str, parent_names: dict[str, str | None]
) -> bool:
    """Filter database objects during autogenerate to only track managed tables."""
    if type_ == "table":
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emits SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_name=include_name,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects to the database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
