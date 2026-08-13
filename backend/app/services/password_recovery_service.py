from datetime import timedelta
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_password_reset_token
from app.exceptions.http_exceptions import NotFoundException
from app.repositories.user_repository import UserRepository
from app.schemas.password_recovery import (
    PasswordRecoveryData,
    PasswordRecoveryRequest,
)
from app.services.email_service import EmailService


class PasswordRecoveryService:
    """Business logic for initiating password recovery."""

    def __init__(
        self,
        db: Session,
        email_service: EmailService | None = None,
    ) -> None:
        self.user_repository = UserRepository(db)
        self.email_service = email_service or EmailService()

    def initiate_password_recovery(
        self,
        payload: PasswordRecoveryRequest,
    ) -> PasswordRecoveryData:
        """Validate the account and send a time-limited password reset email.

        Users accepted the Terms of Use and Privacy Policy at signup; only
        registered accounts may request a reset. The reset link expires after
        PASSWORD_RESET_TOKEN_EXPIRY minutes and cannot be used afterward.
        """
        normalized_email = payload.email.strip().lower()
        user = self.user_repository.get_by_email(normalized_email)

        if user is None:
            raise NotFoundException(
                message="No account is associated with this email address",
                code="USER_NOT_FOUND",
            )

        expires_minutes = settings.PASSWORD_RESET_TOKEN_EXPIRY
        reset_token = create_password_reset_token(
            user_id=str(user.id),
            email=normalized_email,
            expires_delta=timedelta(minutes=expires_minutes),
        )
        reset_link = self._build_reset_link(reset_token)

        self.email_service.send_password_reset_email(
            to_email=normalized_email,
            reset_link=reset_link,
            expires_minutes=expires_minutes,
        )

        return PasswordRecoveryData(
            email=normalized_email,
            expires_in=expires_minutes * 60,
        )

    @staticmethod
    def _build_reset_link(token: str) -> str:
        base = settings.FRONTEND_URL.rstrip("/")
        query = urlencode({"token": token})
        return f"{base}/reset-password?{query}"
