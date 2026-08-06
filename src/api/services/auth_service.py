"""Authentication service layer."""

from sqlalchemy.orm import Session

from src.api.models.user import User
from src.config.settings import Settings, get_settings
from src.exceptions import UnauthorizedError
from src.utils.password import verify_password
from src.utils.validation import normalize_email

__all__ = ["authenticate_user", "login_user"]


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Return the user when credentials are valid, otherwise None."""
    try:
        normalized_email = normalize_email(email)
    except ValueError:
        return None

    user = db.query(User).filter(User.email == normalized_email).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def login_user(
    db: Session,
    *,
    email: str,
    password: str,
    remember_me: bool = False,
    settings: Settings | None = None,
) -> tuple[User, int]:
    """Authenticate a user and return the user with token lifetime in seconds."""
    runtime_settings = settings or get_settings()
    user = authenticate_user(db, email, password)
    if user is None:
        raise UnauthorizedError(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
        )

    expires_in = (
        runtime_settings.effective_remember_me_jwt_expiry
        if remember_me
        else runtime_settings.effective_jwt_expiry
    )
    return user, expires_in
