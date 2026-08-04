import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from config.database import normalize_database_url

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _get_test_database_url() -> str | None:
    for env_file in (PROJECT_ROOT / ".env.test", PROJECT_ROOT / ".env"):
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith("DATABASE_URL="):
                return normalize_database_url(line.split("=", 1)[1].strip())
            if line.startswith("DB_URL="):
                return normalize_database_url(line.split("=", 1)[1].strip())
    url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    return normalize_database_url(url)


def _run_alembic(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    database_url = _get_test_database_url()
    if database_url:
        env["DATABASE_URL"] = database_url

    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def database_url() -> str:
    url = _get_test_database_url()
    if not url:
        pytest.skip("DATABASE_URL is not configured for migration tests")
    return url


def _reset_database(database_url: str) -> None:
    """Drop managed tables and Alembic state for a clean migration run."""
    import asyncio

    async def _drop_managed_objects() -> None:
        engine = create_async_engine(database_url)
        async with engine.begin() as connection:
            await connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            await connection.execute(
                text("DROP TABLE IF EXISTS alembic_version CASCADE")
            )
        await engine.dispose()

    asyncio.run(_drop_managed_objects())


@pytest.fixture(scope="module")
def migrated_database(database_url: str):
    """Ensure migrations are applied before schema assertions."""
    _reset_database(database_url)

    upgrade_result = _run_alembic("upgrade", "head")
    if upgrade_result.returncode != 0:
        pytest.fail(
            "Failed to apply migrations: "
            f"{upgrade_result.stderr or upgrade_result.stdout}"
        )

    yield database_url

    _run_alembic("downgrade", "base")


# ---- Structural validation ----


def test_initial_migration_module_is_valid():
    migration_path = (
        PROJECT_ROOT / "alembic" / "versions" / "001_initial_migration.py"
    )
    spec = importlib.util.spec_from_file_location(
        "initial_migration", migration_path
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    assert migration.revision == "001_initial"
    assert migration.down_revision is None
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)


def test_second_migration_module_is_valid():
    migration_path = (
        PROJECT_ROOT / "alembic" / "versions" / "002_add_is_confirmed_to_users.py"
    )
    spec = importlib.util.spec_from_file_location(
        "second_migration", migration_path
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    assert migration.revision == "002_add_is_confirmed"
    assert migration.down_revision == "001_initial"
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)


def test_third_migration_module_is_valid():
    migration_path = (
        PROJECT_ROOT / "alembic" / "versions" / "003_add_profile_fields_to_users.py"
    )
    spec = importlib.util.spec_from_file_location(
        "third_migration", migration_path
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    assert migration.revision == "003_add_profile_fields"
    assert migration.down_revision == "002_add_is_confirmed"
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)


def test_alembic_versions_directory_exists():
    versions_dir = PROJECT_ROOT / "alembic" / "versions"
    assert versions_dir.is_dir()
    py_files = list(versions_dir.glob("*.py"))
    real_migrations = [f for f in py_files if f.name != "__init__.py"]
    assert len(real_migrations) >= 3, "Expected at least three migration scripts"


def test_alembic_env_file_exists():
    assert (PROJECT_ROOT / "alembic" / "env.py").is_file()


def test_alembic_ini_exists():
    assert (PROJECT_ROOT / "alembic.ini").is_file()


def test_script_template_exists():
    assert (PROJECT_ROOT / "alembic" / "script.py.mako").is_file()


# ---- Upgrade / downgrade integration ----


def test_alembic_upgrade_head(migrated_database: str):
    current = _run_alembic("current")
    assert current.returncode == 0
    assert "003_add_profile_fields" in current.stdout


async def test_users_table_exists_after_migration(migrated_database: str):
    engine = create_async_engine(migrated_database)
    async with engine.connect() as connection:
        table_names = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        assert "users" in table_names

        columns = await connection.run_sync(
            lambda sync_conn: {
                column["name"]
                for column in inspect(sync_conn).get_columns("users")
            }
        )
        assert columns == {
            "id",
            "email",
            "hashed_password",
            "is_confirmed",
            "first_name",
            "last_name",
            "mobile_number",
            "bio",
            "address",
            "profile_picture",
            "created_at",
            "updated_at",
        }

        result = await connection.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE tablename = 'users' AND indexname = 'ix_users_email'"
            )
        )
        assert result.scalar_one_or_none() == "ix_users_email"

    await engine.dispose()


async def test_users_table_column_types(migrated_database: str):
    engine = create_async_engine(migrated_database)
    async with engine.connect() as connection:
        columns = await connection.run_sync(
            lambda sync_conn: {
                col["name"]: col
                for col in inspect(sync_conn).get_columns("users")
            }
        )
        assert columns["id"]["autoincrement"] is True
        assert columns["email"]["nullable"] is False
        assert columns["hashed_password"]["nullable"] is False
        assert columns["is_confirmed"]["nullable"] is False
        assert columns["created_at"]["nullable"] is False
        assert columns["updated_at"]["nullable"] is False

    await engine.dispose()


async def test_users_email_unique_constraint(migrated_database: str):
    engine = create_async_engine(migrated_database)
    async with engine.connect() as connection:
        indexes = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).get_indexes("users")
        )
        email_idx = next(
            (idx for idx in indexes if "email" in idx.get("column_names", [])),
            None,
        )
        assert email_idx is not None, "Expected index on email column"
        assert email_idx.get("unique") is True

    await engine.dispose()


def test_alembic_downgrade_removes_users_table(database_url: str):
    _reset_database(database_url)

    upgrade_result = _run_alembic("upgrade", "head")
    assert upgrade_result.returncode == 0

    downgrade_result = _run_alembic("downgrade", "base")
    assert downgrade_result.returncode == 0

    current = _run_alembic("current")
    assert current.returncode == 0
    assert "001_initial" not in current.stdout

    import asyncio

    async def _assert_users_table_missing() -> None:
        engine = create_async_engine(database_url)
        async with engine.connect() as connection:
            table_names = await connection.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
            assert "users" not in table_names
        await engine.dispose()

    asyncio.run(_assert_users_table_missing())

    _run_alembic("upgrade", "head")


def test_alembic_downgrade_single_step(database_url: str):
    _reset_database(database_url)

    upgrade_result = _run_alembic("upgrade", "head")
    assert upgrade_result.returncode == 0

    result = _run_alembic("downgrade", "-1")
    assert result.returncode == 0

    restore_result = _run_alembic("upgrade", "head")
    assert restore_result.returncode == 0


def test_alembic_history_shows_revisions():
    result = _run_alembic("history", "--verbose")
    assert result.returncode == 0
    assert "001_initial" in result.stdout
    assert "002_add_is_confirmed" in result.stdout
    assert "003_add_profile_fields" in result.stdout


# ---- Migration config module ----


def test_migration_config_get_project_root():
    from config.migrations import get_project_root

    root = get_project_root()
    assert (root / "alembic.ini").exists()
    assert (root / "alembic").is_dir()


def test_migration_config_get_alembic_config():
    from config.migrations import get_alembic_config

    cfg = get_alembic_config()
    assert cfg.get_main_option("script_location") == "alembic"


def test_migration_config_normalize_database_url():
    from config.database import normalize_database_url

    assert normalize_database_url(None) is None
    assert (
        normalize_database_url("postgresql://u:p@h/d")
        == "postgresql+asyncpg://u:p@h/d"
    )
    assert (
        normalize_database_url("postgres://u:p@h/d")
        == "postgresql+asyncpg://u:p@h/d"
    )
    assert (
        normalize_database_url("postgresql+asyncpg://u:p@h/d")
        == "postgresql+asyncpg://u:p@h/d"
    )
    assert normalize_database_url("sqlite:///test.db") == "sqlite:///test.db"
