"""Authentication service layer."""

from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService, get_auth0_service
from src.config.settings import Settings, get_settings
from src.exceptions import UnauthorizedError
from src.utils.password import verify_password
from src.utils.validation import normalize_email

__all__ = ["authenticate_user", "login_user"]

_POST_LOGIN_REDIRECT = "/dashboard"


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


def _resolve_local_user(db: Session, email: str) -> User:
    """Load an active local user record by email or raise UnauthorizedError."""
    try:
        normalized_email = normalize_email(email)
    except ValueError as exc:
        raise UnauthorizedError(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
        ) from exc

    user = db.query(User).filter(User.email == normalized_email).first()
    if user is None or not user.is_active:
        raise UnauthorizedError(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
        )
    return user


def login_user(
    db: Session,
    *,
    email: str,
    password: str,
    remember_me: bool = False,
    settings: Settings | None = None,
    auth0_service: Auth0AuthenticationService | None = None,
) -> tuple[User, int]:
    """Authenticate a user and return the user with token lifetime in seconds."""
    runtime_settings = settings or get_settings()
    auth0 = auth0_service or get_auth0_service(runtime_settings)

    if auth0.is_enabled:
        auth0.authenticate(email, password)
        user = _resolve_local_user(db, email)
    else:
        user = authenticate_user(db, email, password)
        if user is None:
            raise UnauthorizedError(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )
        if not user.is_active:
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


def build_login_response_data(user: User, *, access_token: str, expires_in: int) -> dict:
    """Build the login success payload shared with the frontend."""
    return {
        "id": str(user.id),
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "title": "Welcome back",
        "message": "You have signed in successfully.",
        "description": "Everything you need to create standout real estate content.",
        "link": _POST_LOGIN_REDIRECT,
        "redirect": _POST_LOGIN_REDIRECT,
    }


def build_session_response_data(user: User) -> dict:
    """Build the session payload shared with the frontend."""
    return {
        "id": str(user.id),
        "email": user.email,
        "title": "Session active",
        "message": "Your session is active.",
        "description": "You are signed in to Agentwise.",
        "link": _POST_LOGIN_REDIRECT,
        "redirect": _POST_LOGIN_REDIRECT,
    }
