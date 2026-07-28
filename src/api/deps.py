from collections.abc import Generator

from sqlalchemy.orm import Session

from src.database import get_db as _get_db
from src.services.auth_service import AuthService
from src.services.auth_service import get_auth_service as _get_auth_service


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_auth_service() -> AuthService:
    return _get_auth_service()
