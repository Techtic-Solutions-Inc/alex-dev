"""Centralized application logging configuration."""

import logging

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured, process-wide console logging once at startup."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
