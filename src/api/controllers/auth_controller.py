from sqlalchemy.ext.asyncio import AsyncSession

from models.schema import (
    ConfirmEmailResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from api.services.registration_service import create_registered_user
from services.auth import confirm_email, login_user


async def handle_register(
    body: RegisterRequest, db: AsyncSession
) -> RegisterResponse:
    """Handle user registration request."""
    return await create_registered_user(body, db)


async def handle_login(
    body: LoginRequest, db: AsyncSession
) -> LoginResponse:
    """Handle user login request."""
    return await login_user(body, db)


async def handle_confirm_email(
    token: str, db: AsyncSession
) -> ConfirmEmailResponse:
    """Handle email confirmation request."""
    return await confirm_email(token, db)
