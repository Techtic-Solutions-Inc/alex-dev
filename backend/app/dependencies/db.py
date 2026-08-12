from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    yield from _get_db()
