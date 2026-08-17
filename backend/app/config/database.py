"""Database configuration accessors."""

from app.core.config import get_settings


def get_database_url(*, for_test: bool = False) -> str:
    """Return the configured async PostgreSQL URL, optionally for isolated tests."""
    settings = get_settings()
    if for_test and settings.test_database_url:
        return settings.test_database_url
    return settings.database_url
