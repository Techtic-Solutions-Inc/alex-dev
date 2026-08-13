import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.http_exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.profile import ChangePasswordRequest, ProfileUpdateRequest
from app.schemas.user import SignInRequest, SignupRequest


class AuthService:
    """Business logic for authentication and profile flows."""

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

    def authenticate_user(self, payload: SignInRequest) -> tuple[User, dict[str, str | int]]:
        """Validate credentials and return the user plus JWT access token."""
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

        token_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expiry_minutes * 60,
        }
        return user, token_data

    def get_profile(self, user_id: str) -> User:
        """Return the authenticated user's profile record."""
        user = self._get_user_or_404(user_id)
        return user

    def update_profile(self, user_id: str, payload: ProfileUpdateRequest) -> User:
        """Update profile fields for the authenticated user."""
        user = self._get_user_or_404(user_id)
        normalized_email = payload.email.strip().lower()

        existing = self.user_repository.get_by_email(normalized_email)
        if existing is not None and existing.id != user.id:
            raise BadRequestException(
                message="An account with this email already exists",
                code="EMAIL_ALREADY_EXISTS",
            )

        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.email = normalized_email
        user.username = normalized_email
        user.mobile_number = payload.mobile_number
        user.bio = payload.bio
        user.address_street = payload.address.street
        user.address_city = payload.address.city
        user.address_state = payload.address.state
        user.address_zip = payload.address.zip
        user.address_country = payload.address.country
        user.time_zone = payload.time_zone

        return self.user_repository.update(user)

    def change_password(self, user_id: str, payload: ChangePasswordRequest) -> User:
        """Change the authenticated user's password after verifying the current one."""
        user = self._get_user_or_404(user_id)

        if not verify_password(payload.current_password, user.hashed_password):
            raise BadRequestException(
                message="Current password is incorrect",
                code="INCORRECT_CURRENT_PASSWORD",
            )

        if payload.current_password == payload.new_password:
            raise BadRequestException(
                message="New password must be different from the current password",
                code="PASSWORD_UNCHANGED",
            )

        return self.user_repository.update_password(
            user,
            hash_password(payload.new_password),
        )

    def _get_user_or_404(self, user_id: str) -> User:
        try:
            parsed_id = uuid.UUID(str(user_id))
        except ValueError as exc:
            raise NotFoundException(
                message="User not found",
                code="USER_NOT_FOUND",
            ) from exc

        user = self.user_repository.get_by_id(parsed_id)
        if user is None:
            raise NotFoundException(
                message="User not found",
                code="USER_NOT_FOUND",
            )
        return user
