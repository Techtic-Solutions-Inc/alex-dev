"""Compatibility exports for environment and database configuration."""

from app.config.database import get_database_url

__all__ = ["get_database_url"]
