import os
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine, text

from config.database import normalize_database_url


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_migration_environment() -> None:
    """Load environment variables required for Alembic migrations."""
    project_root = get_project_root()
    load_dotenv(project_root / ".env")
    load_dotenv(project_root / ".env.test", override=False)
    load_dotenv(project_root / "src" / ".env", override=False)


def _get_database_url() -> str:
    load_migration_environment()
    url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not configured; cannot run migrations. "
            "Set DATABASE_URL or DB_URL in .env, src/.env, or the environment."
        )
    return url


def _get_sync_url(url: str) -> str:
    """Convert an async driver URL to a sync one for Alembic inspection."""
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


def get_alembic_config() -> Config:
    """Build Alembic configuration with absolute paths and database URL."""
    project_root = get_project_root()
    ini_path = project_root / "alembic.ini"
    if not ini_path.exists():
        raise FileNotFoundError(
            f"Alembic configuration not found at {ini_path}. "
            "Run from the project root directory."
        )
    config = Config(str(ini_path))

    database_url = normalize_database_url(_get_database_url())
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)

    return config


def run_migrations() -> None:
    """Apply all pending Alembic migrations up to head."""
    _get_database_url()
    logger.info("Running database migrations")
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed")


def downgrade_migrations(revision: str = "-1") -> None:
    """Roll back migrations to a given revision (default: one step back)."""
    _get_database_url()
    logger.info("Downgrading database to revision: {}", revision)
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    logger.info("Database downgrade completed")


def get_current_revision() -> Optional[str]:
    """Return the current migration revision applied to the database."""
    database_url = _get_database_url()
    sync_url = _get_sync_url(normalize_database_url(database_url) or database_url)
    engine = create_engine(sync_url)
    try:
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    finally:
        engine.dispose()


def get_head_revision() -> Optional[str]:
    """Return the latest revision available in the migration scripts."""
    alembic_cfg = get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def get_pending_migrations() -> list[str]:
    """Return a list of revision IDs that have not yet been applied."""
    current = get_current_revision()
    alembic_cfg = get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)

    pending = []
    for rev in script.walk_revisions("head", current or "base"):
        if rev.revision != current:
            pending.append(rev.revision)
    return list(reversed(pending))


def has_pending_migrations() -> bool:
    """Check whether there are unapplied migration scripts."""
    return len(get_pending_migrations()) > 0


def _get_applied_revisions(
    script: ScriptDirectory, current: Optional[str]
) -> set[str]:
    """Walk from the current revision back to base to find all applied revisions."""
    applied: set[str] = set()
    if not current:
        return applied
    for rev in script.walk_revisions(current, "base"):
        applied.add(rev.revision)
    return applied


def get_migration_history() -> list[dict]:
    """Return the full history of migration scripts with metadata."""
    alembic_cfg = get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)
    current = get_current_revision()
    applied = _get_applied_revisions(script, current)

    history = []
    for rev in script.walk_revisions():
        history.append({
            "revision": rev.revision,
            "down_revision": rev.down_revision,
            "description": rev.doc,
            "is_applied": rev.revision in applied,
            "is_current": rev.revision == current,
        })
    return list(reversed(history))


def stamp_revision(revision: str = "head") -> None:
    """Stamp the database with a specific revision without running migrations."""
    _get_database_url()
    logger.info("Stamping database at revision: {}", revision)
    alembic_cfg = get_alembic_config()
    command.stamp(alembic_cfg, revision)
    logger.info("Database stamped successfully")


def generate_revision(message: str, autogenerate: bool = True) -> str:
    """Create a new migration revision script. Returns the revision ID."""
    _get_database_url()
    logger.info("Generating migration revision: {}", message)
    alembic_cfg = get_alembic_config()
    rev = command.revision(
        alembic_cfg,
        message=message,
        autogenerate=autogenerate,
    )
    if rev is None:
        raise RuntimeError(
            "Alembic failed to generate a revision. Check the migration "
            "configuration and database connectivity."
        )
    logger.info("Generated migration revision: {}", rev.revision)
    return rev.revision


def check_database_connectivity() -> bool:
    """Verify that the database is reachable."""
    try:
        database_url = _get_database_url()
        sync_url = _get_sync_url(
            normalize_database_url(database_url) or database_url
        )
        engine = create_engine(sync_url)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        finally:
            engine.dispose()
    except Exception as exc:
        logger.debug("Database connectivity check failed: {}", exc)
        return False
