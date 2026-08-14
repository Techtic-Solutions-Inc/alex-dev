import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    """Configure Loguru with file rotation and console output."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )
    logger.add(
        str(LOG_DIR / "{time:YYYY-MM-DD}.log"),
        rotation="1 day",
        retention="30 days",
        level=settings.LOG_LEVEL,
        encoding="utf-8",
        format="{time} {level} {message}",
    )
