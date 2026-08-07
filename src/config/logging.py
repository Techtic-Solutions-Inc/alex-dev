"""Logging configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

from src.config.settings import get_settings

settings = get_settings()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

logger.add(
    "logs/{time:YYYY-MM-DD}.log",
    rotation="1 day",
    level=settings.log_level,
    format="{time} {level} {message}",
)
