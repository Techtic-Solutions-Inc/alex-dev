"""Authentication service layer."""

from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService, get_auth0_service
from src.config.settings import Settings, get_settings
from src.exceptions import ConflictError
from src.utils.password import verify_password
from src.utils.validation import normalize_email

__all__ = [
    "authenticate_user",
    "build_login_response_data",
    "build_session_response_data",
    "login_user",
]

_POST_LOGIN_REDIRECT = "/dashboard"
_INCORRECT_PASSWORD_MESSAGE = "Incorrect email or password."
_INCORRECT_PASSWORD_CODE = "INCORRECT_PASSWORD"


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
    """Load an active local user record by email or raise ConflictError."""
    try:
        normalized_email = normalize_email(email)
    except ValueError as exc:
        raise ConflictError(
            message=_INCORRECT_PASSWORD_MESSAGE,
            code=_INCORRECT_PASSWORD_CODE,
        ) from exc

    user = db.query(User).filter(User.email == normalized_email).first()
    if user is None or not user.is_active:
        raise ConflictError(
            message=_INCORRECT_PASSWORD_MESSAGE,
            code=_INCORRECT_PASSWORD_CODE,
        )
    return user


def _raise_incorrect_password() -> None:
    """Raise the standard incorrect-password conflict error."""
    raise ConflictError(
        message=_INCORRECT_PASSWORD_MESSAGE,
        code=_INCORRECT_PASSWORD_CODE,
    )


def login_user(
    db: Session,
    *,
    email: str,
    password: str,
    remember_me: bool = False,
    settings: Settings | None = None,
    auth0_service: Auth0AuthenticationService | None = None,
) -> tuple[User, int]:
    """Authenticate a user and return the user with token lifetime in seconds.

    When Auth0 is configured, credentials are validated against Auth0 first.
    Incorrect password attempts return HTTP 409 with ``INCORRECT_PASSWORD``.
    """
    runtime_settings = settings or get_settings()
    auth0 = auth0_service or get_auth0_service(runtime_settings)

    if auth0.is_enabled:
        auth0.authenticate(email, password)
        user = _resolve_local_user(db, email)
    else:
        try:
            normalized_email = normalize_email(email)
        except ValueError as exc:
            raise ConflictError(
                message=_INCORRECT_PASSWORD_MESSAGE,
                code=_INCORRECT_PASSWORD_CODE,
            ) from exc

        user = db.query(User).filter(User.email == normalized_email).first()
        if user is None or not user.is_active:
            _raise_incorrect_password()
        if not verify_password(password, user.password_hash):
            _raise_incorrect_password()

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
