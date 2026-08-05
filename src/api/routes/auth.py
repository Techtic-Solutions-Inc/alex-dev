from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers.auth_controller import (
    handle_confirm_email,
    handle_login,
    handle_register,
)
from api.middlewares.rate_limiter import limiter
from config.database import get_db_session
from models.schema import (
    ConfirmEmailRequest,
    ConfirmEmailResponse,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Weak password"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
        503: {"model": ErrorResponse, "description": "Email service unavailable"},
    },
    summary="Register a new user",
    description=(
        "Register a new user with a unique email and strong password. "
        "A confirmation email is sent upon successful registration."
    ),
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> RegisterResponse:
    """Register a new user with email and password."""
    return await handle_register(body, db)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
    summary="Authenticate user",
    description="Authenticate with email and password to receive a JWT session token.",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    """Authenticate a user with email and password."""
    return await handle_login(body, db)


@router.post(
    "/confirm",
    response_model=ConfirmEmailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Confirm email address",
    description="Confirm a user's email address using the token from the confirmation email.",
)
async def confirm(
    body: ConfirmEmailRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ConfirmEmailResponse:
    """Confirm a user's email address using the token from the confirmation email."""
    return await handle_confirm_email(body.token, db)
