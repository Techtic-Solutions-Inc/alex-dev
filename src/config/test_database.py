"""Test database configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base, to_sync_database_url
from src.config.settings import get_settings

settings = get_settings()
DATABASE_URL_TEST = settings.database_url_test or settings.database_url

SYNC_TEST_DATABASE_URL = to_sync_database_url(DATABASE_URL_TEST)

connect_args = (
    {"check_same_thread": False}
    if SYNC_TEST_DATABASE_URL.startswith("sqlite")
    else {}
)

test_engine = create_engine(
    SYNC_TEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def create_test_tables() -> None:
    """Create all tables in the test database."""
    import src.api.models  # noqa: F401

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def drop_test_tables() -> None:
    """Drop all tables in the test database."""
    Base.metadata.drop_all(bind=test_engine)
