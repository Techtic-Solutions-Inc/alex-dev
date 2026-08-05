from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils.password import validate_password_strength


def validate_password(password: str) -> None:
    """Validate password strength, raising HTTPException on failure."""
    try:
        validate_password_strength(password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None


async def validate_email_not_registered(email: str, db: AsyncSession) -> None:
    """Ensure the email is not already taken, raising HTTPException if it is."""
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )


async def validate_registration_input(
    email: str, password: str, db: AsyncSession
) -> None:
    """Run all registration validations: password strength and email uniqueness."""
    validate_password(password)
    await validate_email_not_registered(email, db)
