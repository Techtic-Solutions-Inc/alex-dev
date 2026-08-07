"""Authentication service layer."""

from sqlalchemy.orm import Session

from src.api.models.user import User
from src.utils.password import verify_password

__all__ = ["authenticate_user"]


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Return the user when credentials are valid, otherwise None."""
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None
