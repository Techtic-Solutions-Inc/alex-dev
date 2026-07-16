import secrets
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.api.v1.models.password_reset_token import PasswordResetToken
from src.api.v1.models.user import User
from src.api.v1.schemas.auth import (
    LoginRequest,
    RequestPasswordResetRequest,
    RequestPasswordResetResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from src.config import settings
from src.services.email_service import EmailService


class AuthService:
    def __init__(self, db: Session, email_service: EmailService | None = None):
        self.db = db
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.email_service = email_service or EmailService()

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user or not self.pwd_context.verify(request.password, user.hashed_password):
            raise ValueError('Invalid credentials')
        return TokenResponse(access_token='dummy_token')

    def validate_reset_token(self, token: str) -> PasswordResetToken:
        reset_token = self._get_valid_reset_token(token)
        if reset_token is None:
            raise ValueError('Invalid or expired reset link')
        return reset_token

    async def request_password_reset(
        self,
        request: RequestPasswordResetRequest,
    ) -> RequestPasswordResetResponse:
        user = self.db.query(User).filter(User.email == request.email).first()
        if user is None:
            return RequestPasswordResetResponse()

        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS,
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_value,
            expires_at=expires_at,
        )
        self.db.add(reset_token)
        self.db.commit()

        reset_link = f'{settings.PASSWORD_RESET_API_URL}?token={token_value}'
        self.email_service.send_password_reset_email(user.email, reset_link)

        return RequestPasswordResetResponse()

    async def reset_password(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        if request.new_password != request.confirm_password:
            raise ValueError('Passwords do not match')

        reset_token = self._get_valid_reset_token(request.token)
        if reset_token is None:
            raise ValueError('Invalid or expired reset link')

        user = self.db.query(User).filter(User.id == reset_token.user_id).first()
        if user is None:
            raise ValueError('Invalid or expired reset link')

        user.hashed_password = self.pwd_context.hash(request.new_password)
        reset_token.used_at = datetime.now(timezone.utc)
        self.db.commit()

        return ResetPasswordResponse()

    def _get_valid_reset_token(self, token: str) -> PasswordResetToken | None:
        reset_token = (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )
        return reset_token
