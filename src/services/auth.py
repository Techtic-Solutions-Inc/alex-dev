from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.schema import (
    ConfirmEmailResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from models.user import User
from utils.password import hash_password, validate_password_strength, verify_password
from utils.token import (
    decode_confirmation_token,
    generate_session_token,
)


async def register_user(
    body: RegisterRequest,
    db: AsyncSession,
) -> RegisterResponse:
    """Register a new user in the database.

    Validates password strength and email uniqueness before persisting the
    user.  Email confirmation dispatching is handled by the API-layer
    registration service.
    """
    try:
        validate_password_strength(body.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    email = body.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    user = User(
        email=email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)

    try:
        await db.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        ) from None

    return RegisterResponse(
        email=user.email,
        message="Registration successful. Please check your email to confirm your account.",
    )


async def confirm_email(
    token: str,
    db: AsyncSession,
) -> ConfirmEmailResponse:
    """Confirm a user's email address using the token from the confirmation email."""
    try:
        email = decode_confirmation_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.is_confirmed:
        return ConfirmEmailResponse(
            email=user.email,
            message="Email already confirmed.",
        )

    user.is_confirmed = True
    await db.flush()

    return ConfirmEmailResponse(
        email=user.email,
        message="Email confirmed successfully.",
    )


async def login_user(
    body: LoginRequest,
    db: AsyncSession,
) -> LoginResponse:
    """Authenticate a user and return a session token."""
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
