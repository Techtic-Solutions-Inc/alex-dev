"""Authentication and JWT token service."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.exceptions import InvalidCredentialsError
from src.models.user import User
from src.services.user_service import UserService
from src.utils.password import verify_password

logger = logging.getLogger(__name__)


class AuthService:
    """Handles credential verification and JWT issuance."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_service = UserService(db)
        self.settings = get_settings()

    def authenticate_user(self, email: str, password: str) -> User:
        """Verify credentials and return the authenticated user."""
        user = self.user_service.get_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            logger.warning("Failed login attempt for email: %s", email.lower())
            raise InvalidCredentialsError()

        logger.info("Successful login for email: %s", user.email)
        return user

    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Generate a signed JWT access token."""
        expire = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta is not None
            else timedelta(minutes=self.settings.JWT_EXPIRATION_MINUTES)
        )
        payload: dict[str, Any] = {
            "sub": subject,
            "exp": expire,
        }
        return jwt.encode(
            payload,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT access token."""
        return jwt.decode(
            token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.JWT_ALGORITHM],
        )
