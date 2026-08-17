"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pymongo.database import Database

from app.db.mongo import get_database
from app.repositories.users import UserRepository
from app.schemas.auth import (
    EmailVerificationData,
    LoginRequest,
    RefreshRequest,
    SignupData,
    SignupRequest,
    TokenData,
)
from app.schemas.common import ErrorResponse, SuccessResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(
    database: Annotated[Database, Depends(get_database)],
) -> AuthService:
    """Build the auth service for the active request database."""
    return AuthService(UserRepository(database))


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    response_model=SuccessResponse[SignupData],
    responses={
        409: {"model": ErrorResponse, "description": "Email already registered."},
        422: {"model": ErrorResponse, "description": "Validation failed."},
    },
)
def signup(
    payload: SignupRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[SignupData]:
    """Create an account and return an authenticated session."""
    data = service.signup(payload)
    return SuccessResponse(
        message="Account created successfully.",
        data=SignupData(**data),
    )


@router.post(
    "/login",
    summary="Authenticate with email and password",
    response_model=SuccessResponse[TokenData],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials."},
        403: {"model": ErrorResponse, "description": "Account inactive."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
    },
)
def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenData]:
    """Verify credentials and issue rotating session tokens."""
    data = service.login(payload)
    return SuccessResponse(message="Signed in successfully.", data=TokenData(**data))


@router.post(
    "/refresh",
    summary="Rotate a refresh token",
    response_model=SuccessResponse[TokenData],
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token."},
        403: {"model": ErrorResponse, "description": "Account inactive."},
        422: {"model": ErrorResponse, "description": "Validation failed."},
    },
)
def refresh(
    payload: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenData]:
    """Exchange a single-use refresh token for a new session."""
    data = service.refresh(payload.refresh_token)
    return SuccessResponse(message="Session refreshed successfully.", data=TokenData(**data))


@router.post(
    "/verify-email",
    summary="Confirm a user's email address",
    response_model=SuccessResponse[EmailVerificationData],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid verification token."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
)
def verify_email(
    token: str,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[EmailVerificationData]:
    """Mark an email address as verified using a signed token."""
    data = service.verify_email(token)
    return SuccessResponse(
        message="Email verified successfully.",
        data=EmailVerificationData(**data),
    )
