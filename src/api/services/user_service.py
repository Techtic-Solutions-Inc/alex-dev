"""User registration and email confirmation service layer."""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.email_service import send_confirmation_email
from src.config.settings import Settings, get_settings
from src.exceptions import BadRequestError, ConflictError, NotFoundError
from src.utils.password import hash_password
from src.utils.validation import normalize_email, validate_password_strength

__all__ = ["confirm_user_email", "create_user_with_confirmation"]


def _generate_unique_username(db: Session, email: str) -> str:
    """Derive a unique username from the email local part."""
    local_part = email.split("@", maxsplit=1)[0]
    base_username = re.sub(r"[^a-zA-Z0-9_]", "", local_part)[:40] or "user"
    candidate = base_username
    suffix = 1

    while db.query(User).filter(User.username == candidate).first() is not None:
        suffix_text = str(suffix)
        candidate = f"{base_username[:50 - len(suffix_text)]}{suffix_text}"
        suffix += 1

    return candidate


def _create_verification_token(settings: Settings) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.email_verification_token_expire_hours
    )
    return token, expires_at


def create_user_with_confirmation(
    db: Session,
    *,
    email: str,
    password: str,
    settings: Settings | None = None,
) -> tuple[User, str]:
    """Register a user, persist credentials, and send a confirmation email."""
    runtime_settings = settings or get_settings()

    try:
        normalized_email = normalize_email(email)
    except ValueError as exc:
        raise BadRequestError(
            message="Invalid email format.",
            code="INVALID_EMAIL",
        ) from exc

    try:
        validate_password_strength(password)
    except ValueError as exc:
        raise BadRequestError(
            message=str(exc),
            code="WEAK_PASSWORD",
            details={"field": "password"},
        ) from exc

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user is not None:
        raise ConflictError(
            message="An account with this email address already exists.",
            code="EMAIL_ALREADY_EXISTS",
            details={"field": "email"},
        )

    verification_token, token_expires_at = _create_verification_token(runtime_settings)
    user = User(
        username=_generate_unique_username(db, normalized_email),
        email=normalized_email,
        password_hash=hash_password(password),
        is_email_verified=False,
        email_verification_token=verification_token,
        email_verification_token_expires_at=token_expires_at,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            message="An account with this email address already exists.",
            code="EMAIL_ALREADY_EXISTS",
            details={"field": "email"},
        ) from exc

    db.refresh(user)

    confirmation_link = send_confirmation_email(
        recipient_email=user.email,
        confirmation_token=verification_token,
        settings=runtime_settings,
    )
    return user, confirmation_link


def confirm_user_email(db: Session, *, token: str) -> User:
    """Confirm a user's email address using a verification token."""
    normalized_token = token.strip()
    if not normalized_token:
        raise BadRequestError(
            message="A confirmation token is required.",
            code="INVALID_TOKEN",
        )

    user = (
        db.query(User)
        .filter(User.email_verification_token == normalized_token)
        .first()
    )
    if user is None:
        raise NotFoundError(
            message="The confirmation link is invalid or has already been used.",
            code="INVALID_CONFIRMATION_TOKEN",
        )

    if user.is_email_verified:
        raise BadRequestError(
            message="This email address has already been confirmed.",
            code="EMAIL_ALREADY_CONFIRMED",
        )

    expires_at = user.email_verification_token_expires_at
    if expires_at is not None and expires_at < datetime.now(timezone.utc):
        raise BadRequestError(
            message="The confirmation link has expired. Please sign up again.",
            code="CONFIRMATION_TOKEN_EXPIRED",
        )

    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None
    db.commit()
    db.refresh(user)
    return user
