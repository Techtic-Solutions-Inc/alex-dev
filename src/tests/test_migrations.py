import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from config.database import normalize_database_url
from config.migrations import get_head_revision

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_alembic_upgrade_head():
    current = subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert current.returncode == 0, current.stderr
    head = get_head_revision()
    assert head in current.stdout


@pytest.mark.asyncio
async def test_users_table_exists_after_migration(db_session):
    database_url = normalize_database_url(
        __import__("os").getenv("DATABASE_URL") or __import__("os").getenv("DB_URL")
    )
    sync_url = database_url.replace("+asyncpg", "")
    engine = create_engine(sync_url)

    inspector = inspect(engine)
    assert "users" in inspector.get_table_names()

    column_names = {column["name"] for column in inspector.get_columns("users")}
    assert {
        "id",
        "email",
        "hashed_password",
        "is_active",
        "is_confirmed",
        "created_at",
        "updated_at",
    }.issubset(column_names)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar_one() >= 0

    engine.dispose()
