"""JWT authentication middleware."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.config.database import get_db
from src.exceptions import ForbiddenError, UnauthorizedError
from src.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _require_bearer_token(token: str | None) -> str:
    """Return the bearer token or raise ForbiddenError when missing."""
    if not token:
        raise ForbiddenError(
            message="Authentication is required to access this resource.",
            code="FORBIDDEN",
        )
    return token


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Retrieve the current authenticated user ID from the JWT token."""
    bearer_token = _require_bearer_token(token)

    try:
        payload = decode_access_token(bearer_token)
    except UnauthorizedError as exc:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        ) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        )

    return user_id


def get_current_user_record(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Retrieve the authenticated user record from the JWT token."""
    bearer_token = _require_bearer_token(token)

    try:
        payload = decode_access_token(bearer_token)
    except UnauthorizedError as exc:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        ) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        )

    if not user.is_active:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="UNAUTHORIZED",
        )

    return user
