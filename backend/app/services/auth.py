"""Authentication business logic."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.exceptions.http_exceptions import APIException
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, SignupRequest
from app.services.email import EmailService


class AuthService:
    """Coordinates account creation, login, and rotating refresh sessions."""

    def __init__(
        self, repository: UserRepository, email_service: EmailService | None = None
    ) -> None:
        self._repository = repository
        self._email_service = email_service or EmailService()

    def signup(self, payload: SignupRequest) -> dict[str, Any]:
        """Create an account and immediately establish a session."""
        user = self._repository.create_user(
            payload.first_name,
            payload.last_name,
            str(payload.email),
            hash_password(payload.password),
        )
        if user is None:
            raise APIException(
                "An account with this email already exists.",
                409,
                "EMAIL_ALREADY_EXISTS",
                {"email": ["An account already uses this email."]},
            )
        verification_token, _ = create_token(
            user["id"], "email_verification", settings.EMAIL_VERIFICATION_EXPIRY_SECONDS
        )
        self._email_service.send_verification_email(user["email"], verification_token)
        token_data = self._issue_tokens(user)
        return {
            **token_data,
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "name": f"{user['first_name']} {user['last_name']}",
            "email_verified": False,
        }

    def verify_email(self, token: str) -> dict[str, Any]:
        """Validate a verification token and mark the matching email as confirmed."""
        try:
            claims = decode_token(token, "email_verification")
        except ValueError as exc:
            raise APIException(
                "The email verification link is invalid or expired.",
                400,
                "INVALID_VERIFICATION_TOKEN",
            ) from exc

        user = self._repository.get_by_id(claims["sub"])
        if not user:
            raise APIException("User account was not found.", 404, "USER_NOT_FOUND")
        if not user.get("email_verified", False) and not self._repository.verify_email(
            user["id"]
        ):
            raise APIException("User account was not found.", 404, "USER_NOT_FOUND")
        return {
            "id": user["id"],
            "email": user["email"],
            "email_verified": True,
            "name": f"{user['first_name']} {user['last_name']}",
        }

    def login(self, payload: LoginRequest) -> dict[str, Any]:
        """Verify credentials without disclosing account existence."""
        user = self._repository.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.get("password_hash", "")):
            raise APIException(
                "Email or password is incorrect.", 401, "INVALID_CREDENTIALS"
            )
        if not user.get("is_active", False):
            raise APIException("This account is unavailable.", 403, "ACCOUNT_INACTIVE")
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        """Rotate a single-use refresh token, revoking sessions on replay."""
        try:
            claims = decode_token(refresh_token, "refresh")
        except ValueError as exc:
            raise APIException("Refresh token is invalid or expired.", 401, "INVALID_REFRESH_TOKEN") from exc

        user_id, token_id = claims["sub"], claims["jti"]
        if not self._repository.consume_refresh_token(token_id, user_id):
            self._repository.revoke_all_sessions(user_id)
            raise APIException("Refresh token is invalid or expired.", 401, "INVALID_REFRESH_TOKEN")
        user = self._repository.get_by_id(user_id)
        if not user or not user.get("is_active", False):
            raise APIException("This account is unavailable.", 403, "ACCOUNT_INACTIVE")
        return self._issue_tokens(user)

    def _issue_tokens(self, user: dict[str, Any]) -> dict[str, Any]:
        access_token, _ = create_token(user["id"], "access", settings.JWT_EXPIRY_SECONDS)
        refresh_token, refresh_expires_at = create_token(
            user["id"], "refresh", settings.JWT_REFRESH_EXPIRY_SECONDS
        )
        refresh_claims = decode_token(refresh_token, "refresh")
        self._repository.store_refresh_token(
            refresh_claims["jti"], user["id"], refresh_expires_at
        )
        return {
            "access_token": access_token,
            "token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRY_SECONDS,
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "email_verified": user.get("email_verified", False),
            },
        }
