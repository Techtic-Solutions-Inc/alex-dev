import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.models.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from src.api.v1.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class AuthController:
    """HTTP controller layer for authentication operations."""

    def __init__(self, auth_service: AuthService | None = None) -> None:
        self.auth_service = auth_service or AuthService()

    def login(self, payload: LoginRequest, db: Session) -> LoginResponse:
        logger.info("Login attempt for email=%s", payload.email)
        user = self.auth_service.authenticate_user(db, payload.email, payload.password)
        if user is None:
            logger.warning("Login failed: invalid credentials for email=%s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            logger.warning("Login failed: inactive account email=%s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )
        access_token = self.auth_service.create_token_for_user(user)
        logger.info("Login successful for email=%s", payload.email)
        return LoginResponse(access_token=access_token)

    def register(self, payload: RegisterRequest, db: Session) -> RegisterResponse:
        logger.info("Registration attempt for email=%s", payload.email)
        try:
            user = self.auth_service.register_user(db, payload.email, payload.password)
        except ValueError as exc:
            logger.warning("Registration failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except RuntimeError as exc:
            logger.exception("Failed to send confirmation email to %s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registration succeeded but confirmation email could not be sent",
            ) from exc

        logger.info("Registration successful for email=%s", payload.email)
        return RegisterResponse(id=user.id, email=user.email)
