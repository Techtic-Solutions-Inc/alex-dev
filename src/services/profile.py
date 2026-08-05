from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.schema import ProfileDetail, ProfileResponse, ProfileUpdateRequest
from models.user import User


def _display_name(user: User) -> str | None:
    parts = [user.first_name, user.last_name]
    name = " ".join(part for part in parts if part)
    return name or None


def _user_to_profile(user: User) -> ProfileResponse:
    name = _display_name(user)
    detail = ProfileDetail(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        mobile_number=user.mobile_number,
        bio=user.bio,
        address=user.address,
        profile_picture=user.profile_picture,
        name=name,
        description=user.bio,
        link=user.profile_picture,
    )
    return ProfileResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        mobile_number=user.mobile_number,
        bio=user.bio,
        address=user.address,
        profile_picture=user.profile_picture,
        name=name,
        description=user.bio,
        link=user.profile_picture,
        profile=detail,
    )


async def get_user_profile(user: User) -> ProfileResponse:
    """Return profile details for the given user."""
    return _user_to_profile(user)


async def update_user_profile(
    user: User,
    body: ProfileUpdateRequest,
    db: AsyncSession,
) -> ProfileResponse:
    """Apply partial updates to a user's profile and return the updated profile."""
    update_data = body.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = update_data["email"].lower()

        if update_data["email"] != user.email:
            existing = await db.execute(
                select(User).where(User.email == update_data["email"])
            )
            if existing.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered.",
                )

    if update_data:
        await db.execute(
            update(User).where(User.id == user.id).values(**update_data)
        )
        await db.flush()
        await db.commit()

    result = await db.execute(select(User).where(User.id == user.id))
    updated_user = result.scalar_one()

    return _user_to_profile(updated_user)
