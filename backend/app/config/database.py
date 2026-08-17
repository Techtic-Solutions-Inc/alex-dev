"""Database configuration accessors."""

from app.core.config import get_settings


def _to_async_driver(database_url: str) -> str:
    """Normalize sync PostgreSQL URLs to the asyncpg driver used by SQLAlchemy."""
    return database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)


def get_database_url(*, for_test: bool = False) -> str:
    """Return the configured async PostgreSQL URL, optionally for isolated tests."""
    settings = get_settings()
    if for_test and settings.test_database_url:
        return _to_async_driver(settings.test_database_url)
    return _to_async_driver(settings.database_url)
