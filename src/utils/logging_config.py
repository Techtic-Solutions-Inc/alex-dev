import logging
import sys
from logging.config import dictConfig

from src.config.settings import settings


def configure_logging() -> None:
    """Configure structured application logging."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": settings.LOG_FORMAT,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
            },
            "loggers": {
                "uvicorn": {"level": settings.LOG_LEVEL, "propagate": True},
                "uvicorn.error": {"level": settings.LOG_LEVEL, "propagate": True},
                "uvicorn.access": {"level": settings.LOG_LEVEL, "propagate": True},
                "src": {"level": settings.LOG_LEVEL, "propagate": True},
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
