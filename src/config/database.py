"""Database connection module."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config.settings import get_settings

settings = get_settings()


def to_sync_database_url(database_url: str) -> str:
    """Convert async PostgreSQL URLs to sync SQLAlchemy URLs."""
    if database_url.startswith("sqlite"):
        return database_url

    url = database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    ).replace("postgresql+asyncpg:", "postgresql:")

    if url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return url


DATABASE_URL = to_sync_database_url(settings.database_url)

connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
