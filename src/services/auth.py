from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.auth import ResetPasswordRequest, ResetPasswordResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _is_reset_token_expired(user: User) -> bool:
    if user.password_reset_token_expires_at is None:
        return True
    expires_at = user.password_reset_token_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


def validate_reset_token(db: Session, token: str) -> User:
    """Validate a password reset token and return the associated user."""
    user = db.query(User).filter(User.password_reset_token == token).first()
    if user is None or _is_reset_token_expired(user):
        raise ValueError("Invalid or expired reset link")
    return user


def reset_password(db: Session, request: ResetPasswordRequest) -> ResetPasswordResponse:
    """Validate the reset token and update the user's password."""
    if request.new_password != request.confirm_password:
        raise ValueError("Passwords do not match")

    user = validate_reset_token(db, request.token)
    user.hashed_password = hash_password(request.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires_at = None
    db.commit()

    return ResetPasswordResponse()
