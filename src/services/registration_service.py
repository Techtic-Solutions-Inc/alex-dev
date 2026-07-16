import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.config.settings import EMAIL_CONFIRMATION_EXPIRATION_HOURS
from src.models.user import User
from src.schemas.auth import RegisterRequest, RegisterResponse
from src.services.auth_service import hash_password
from src.services.email_service import send_confirmation_email
from src.utils.logger import logger

DUPLICATE_EMAIL_MESSAGE = "Email already in use. Please use a different email address."


class DuplicateEmailError(Exception):
    pass


def _generate_confirmation_token() -> str:
    return secrets.token_urlsafe(32)


def register_user(db: Session, request: RegisterRequest) -> RegisterResponse:
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning("Registration attempt with existing email=%s", request.email)
        raise DuplicateEmailError(DUPLICATE_EMAIL_MESSAGE)

    confirmation_token = _generate_confirmation_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=EMAIL_CONFIRMATION_EXPIRATION_HOURS
    )

    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        email_confirmed=False,
        email_confirmation_token=confirmation_token,
        email_confirmation_token_expires_at=expires_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_confirmation_email(user.email, confirmation_token)
    logger.info("User registered successfully user_id=%s email=%s", user.id, user.email)

    return RegisterResponse(
        message="Registration successful. Please check your email to confirm your account.",
        email=user.email,
    )
