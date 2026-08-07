"""Authentication service layer."""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService, get_auth0_service
from src.api.services.email_service import send_password_reset_email
from src.config.settings import Settings, get_settings
from src.exceptions import BadRequestError, ConflictError, NotFoundError
from src.utils.password import hash_password, verify_password
from src.utils.validation import normalize_email, validate_password_strength

__all__ = [
    "authenticate_user",
    "build_login_response_data",
    "build_session_response_data",
    "get_auth0_service",
    "get_auth0_service_dependency",
    "login_user",
    "request_password_reset",
    "reset_password_with_token",
    "validate_password_recovery_request_fields",
    "validate_password_reset_token",
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


def get_auth0_service_dependency() -> Auth0AuthenticationService:
    """FastAPI dependency that provides the Auth0 authentication service."""
    return get_auth0_service()


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


def validate_password_recovery_request_fields(body: object) -> None:
    """Validate password recovery request fields and raise 400 for invalid values."""
    if not isinstance(body, dict):
        raise BadRequestError(
            message="Invalid request body.",
            code="INVALID_REQUEST_BODY",
        )

    email = body.get("email")
    if email is None or (isinstance(email, str) and not email.strip()):
        raise BadRequestError(
            message="Email is required.",
            code="EMPTY_EMAIL",
            details={"field": "email"},
        )

    if body.get("terms_accepted") is not True:
        raise BadRequestError(
            message="You must accept the Terms of Use and Privacy Policy.",
            code="TERMS_NOT_ACCEPTED",
            details={"field": "terms_accepted"},
        )


def _create_password_reset_token(settings: Settings) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.password_reset_token_expire_minutes
    )
    return token, expires_at


def request_password_reset(
    db: Session,
    *,
    email: str,
    settings: Settings | None = None,
) -> tuple[User, str]:
    """Generate a password reset token and send a reset email."""
    runtime_settings = settings or get_settings()

    try:
        normalized_email = normalize_email(email)
    except ValueError as exc:
        raise BadRequestError(
            message="Invalid email format.",
            code="INVALID_EMAIL",
            details={"field": "email"},
        ) from exc

    user = db.query(User).filter(User.email == normalized_email).first()
    if user is None:
        raise NotFoundError(
            message="No account is registered with this email address.",
            code="EMAIL_NOT_FOUND",
            details={"field": "email"},
        )

    reset_token, token_expires_at = _create_password_reset_token(runtime_settings)
    user.password_reset_token = reset_token
    user.password_reset_token_expires_at = token_expires_at
    db.commit()
    db.refresh(user)

    reset_link = send_password_reset_email(
        recipient_email=user.email,
        recipient_first_name=user.first_name or "there",
        reset_token=reset_token,
        settings=runtime_settings,
    )
    return user, reset_link


def _load_user_by_reset_token(db: Session, token: str) -> User:
    normalized_token = token.strip()
    if not normalized_token:
        raise BadRequestError(
            message="A password reset token is required.",
            code="INVALID_TOKEN",
        )

    user = (
        db.query(User)
        .filter(User.password_reset_token == normalized_token)
        .first()
    )
    if user is None:
        raise NotFoundError(
            message="The password reset link is invalid or has already been used.",
            code="INVALID_RESET_TOKEN",
        )

    expires_at = user.password_reset_token_expires_at
    if expires_at is not None and expires_at < datetime.now(timezone.utc):
        raise BadRequestError(
            message=(
                "The password reset link has expired. "
                "Please request a new password reset."
            ),
            code="RESET_TOKEN_EXPIRED",
        )

    return user


def validate_password_reset_token(db: Session, *, token: str) -> User:
    """Validate a password reset token and return the associated user."""
    return _load_user_by_reset_token(db, token)


def reset_password_with_token(
    db: Session,
    *,
    token: str,
    password: str,
) -> User:
    """Reset a user's password using a valid reset token."""
    user = _load_user_by_reset_token(db, token)

    try:
        validate_password_strength(password)
    except ValueError as exc:
        raise BadRequestError(
            message=str(exc),
            code="WEAK_PASSWORD",
            details={"field": "password"},
        ) from exc

    user.password_hash = hash_password(password)
    user.password_reset_token = None
    user.password_reset_token_expires_at = None
    db.commit()
    db.refresh(user)
    return user
