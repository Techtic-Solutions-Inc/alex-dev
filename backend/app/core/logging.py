"""Centralized structured logging configuration."""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def configure_logging() -> None:
    """Configure application logging once, with console and daily rotating file output."""
    logger = logging.getLogger("app")
    if logger.handlers:
        return

    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    log_directory = Path(__file__).resolve().parents[2] / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        log_directory / "application.log",
        when="midnight",
        backupCount=14,
        encoding="utf-8",
        utc=True,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a child of the configured application logger."""
    configure_logging()
    return logging.getLogger(f"app.{name}")
