"""Database migration helpers."""

from pathlib import Path

from alembic import command
from alembic.config import Config

from src.config.database import Base, engine
from src.config.logging import logger


def run_migrations() -> None:
    """Apply pending Alembic migrations using project settings."""
    root = Path(__file__).resolve().parents[2]
    alembic_cfg = Config(str(root / "alembic.ini"))
    logger.info("Running database migrations")
    command.upgrade(alembic_cfg, "head")
    # Ensure model tables exist even if alembic_version is ahead of actual schema.
    Base.metadata.create_all(bind=engine)
    logger.info("Database migrations complete")
