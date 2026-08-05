from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.registration_service import create_registered_user
from api.validators.auth import validate_registration_input
from models.schema import (
    ConfirmEmailResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from models.user import User
from services.auth import confirm_email
from utils.password import verify_password
from utils.token import decode_confirmation_token, generate_session_token


async def handle_register(
    body: RegisterRequest, db: AsyncSession
) -> RegisterResponse:
    """Handle user registration request."""
    email = body.email.lower()
    await validate_registration_input(email, body.password, db)
    return await create_registered_user(body, db)


async def handle_login(
    body: LoginRequest, db: AsyncSession
) -> LoginResponse:
    """Handle user login request."""
    email = body.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    session_token = generate_session_token(user.id, user.email)
    return LoginResponse(session_token=session_token)


async def handle_confirm_email(
    token: str, db: AsyncSession
) -> ConfirmEmailResponse:
    """Handle email confirmation request."""
    try:
        decode_confirmation_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    return await confirm_email(token, db)
