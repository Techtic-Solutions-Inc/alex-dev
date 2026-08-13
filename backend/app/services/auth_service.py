from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.http_exceptions import (
    BadRequestException,
    ForbiddenException,
    UnauthorizedException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import SignInRequest, SignupRequest


class AuthService:
    """Business logic for authentication flows."""

    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register_user(self, payload: SignupRequest) -> User:
        """Create a new user account from signup data."""
        normalized_email = payload.email.strip().lower()

        if self.user_repository.get_by_email(normalized_email):
            raise BadRequestException(
                message="An account with this email already exists",
                code="EMAIL_ALREADY_EXISTS",
            )

        user = User(
            username=normalized_email,
            email=normalized_email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            hashed_password=hash_password(payload.password),
            is_locked=False,
            role="user",
        )
        return self.user_repository.create(user)

    def authenticate_user(self, payload: SignInRequest) -> dict[str, str | int]:
        """Validate credentials and return a JWT access token."""
        normalized_email = payload.email.strip().lower()
        user = self.user_repository.get_by_email(normalized_email)

        if user is None or not verify_password(
            payload.password, user.hashed_password
        ):
            raise UnauthorizedException(
                message="Incorrect email or password",
                code="INVALID_CREDENTIALS",
            )

        if user.is_locked:
            raise ForbiddenException(
                message="Your account has been locked. Please contact support.",
                code="ACCOUNT_LOCKED",
            )

        expiry_minutes = (
            settings.JWT_REMEMBER_ME_EXPIRY
            if payload.remember_me
            else settings.JWT_EXPIRY
        )
        expires_delta = timedelta(minutes=expiry_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=expires_delta,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expiry_minutes * 60,
        }
