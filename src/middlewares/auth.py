"""JWT authentication middleware."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.config.database import get_db
from src.exceptions import UnauthorizedError
from src.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Retrieve the current authenticated user ID from the JWT token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )
        return user_id
    except HTTPException:
        raise
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        ) from exc


def get_current_user_record(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Retrieve the authenticated user record from the JWT token."""
    try:
        payload = decode_access_token(token)
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

    return user
