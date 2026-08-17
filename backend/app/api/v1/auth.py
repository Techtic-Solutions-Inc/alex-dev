"""Authentication HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
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

_common_errors = {
    400: {"model": ErrorResponse, "description": "Malformed request."},
    401: {"model": ErrorResponse, "description": "Credentials or token are invalid."},
    403: {"model": ErrorResponse, "description": "Account is inactive or forbidden."},
    404: {"model": ErrorResponse, "description": "Requested resource was not found."},
    409: {"model": ErrorResponse, "description": "Email address is already registered."},
    422: {"model": ErrorResponse, "description": "Request fields failed validation."},
    500: {"model": ErrorResponse, "description": "Unexpected server error."},
}


def get_auth_service(
    database: Annotated[Database, Depends(get_database)],
) -> AuthService:
    """Build the authentication service for one request."""
    return AuthService(UserRepository(database))


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Register a user account",
    description=(
        "Public endpoint that creates an account with a unique email address, sends a "
        "verification email, and returns bearer tokens. The password is validated and "
        "stored only as a salted hash; it is never included in a response."
    ),
    response_model=SuccessResponse[SignupData],
    responses=_common_errors,
)
def signup(
    body: SignupRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[SignupData]:
    """Register a new user from the documented JSON request body."""
    return SuccessResponse(message="Account created.", data=service.signup(body))


@router.get(
    "/verify-email",
    summary="Verify a registered email address",
    description=(
        "Public endpoint used by the signed link in the verification email. The token "
        "must be an unexpired email-verification token issued during registration. "
        "Calling this endpoint more than once is safe."
    ),
    response_model=SuccessResponse[EmailVerificationData],
    responses=_common_errors,
)
def verify_email(
    token: Annotated[
        str,
        Query(
            min_length=1,
            description="Signed email-verification token from the verification email.",
            examples=["eyJhbGciOiJIUzI1NiIs..."],
        ),
    ],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[EmailVerificationData]:
    """Confirm ownership of the email address associated with a signed token."""
    return SuccessResponse(
        message="Email address verified successfully.", data=service.verify_email(token)
    )


@router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    summary="Create a user session",
    description=(
        "Public Sign In endpoint. Validates the email address and password policy, "
        "verifies the credentials for an active account, then issues a short-lived "
        "JWT access token and a rotating refresh token. Invalid credentials do not "
        "reveal whether an account exists. No authorization header is required."
    ),
    response_model=SuccessResponse[TokenData],
    responses=_common_errors,
)
def login(
    body: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenData]:
    """Authenticate a user using the typed Swagger-visible login form."""
    return SuccessResponse(message="Signed in successfully.", data=service.login(body))


@router.post(
    "/refresh",
    summary="Rotate a refresh token",
    description=(
        "Consumes one valid refresh token and returns a new access/refresh pair. "
        "Replay detection revokes all active refresh sessions for the account."
    ),
    response_model=SuccessResponse[TokenData],
    responses=_common_errors,
)
def refresh(
    body: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenData]:
    """Rotate an existing session using a Swagger-visible JSON request body."""
    return SuccessResponse(
        message="Session refreshed successfully.", data=service.refresh(body.refresh_token)
    )
