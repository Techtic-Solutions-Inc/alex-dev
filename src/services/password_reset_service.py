from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.user import User
from src.services.auth_service import hash_password

EXPIRED_TOKEN_MESSAGE = (
    "This link has expired. Please request a new password reset link."
)
PASSWORD_RESET_REQUEST_PATH = "/auth/forgot-password"
INVALID_TOKEN_MESSAGE = "Invalid or expired reset link."


class TokenExpiredError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def _is_token_expired(user: User) -> bool:
    if user.password_reset_token_expires_at is None:
        return True
    expires_at = user.password_reset_token_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


def get_user_by_reset_token(db: Session, token: str) -> User | None:
    return db.query(User).filter(User.password_reset_token == token).first()


def validate_password_reset_token(db: Session, token: str) -> User:
    user = get_user_by_reset_token(db, token)
    if not user:
        raise InvalidTokenError(INVALID_TOKEN_MESSAGE)
    if _is_token_expired(user):
        raise TokenExpiredError(EXPIRED_TOKEN_MESSAGE)
    return user


def reset_password(db: Session, token: str, new_password: str) -> None:
    user = validate_password_reset_token(db, token)
    user.hashed_password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_token_expires_at = None
    db.commit()
