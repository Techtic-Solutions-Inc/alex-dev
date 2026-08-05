from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers.profile_controller import handle_get_profile, handle_update_profile
from api.middlewares.auth import get_current_user
from config.database import get_db_session
from models.schema import ErrorResponse, ProfileResponse, ProfileUpdateRequest
from models.user import User

router = APIRouter()


@router.get(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        403: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="Get user profile",
    description="Retrieve profile details for the currently authenticated user.",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    """Return the authenticated user's profile."""
    return await handle_get_profile(current_user)


@router.put(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        403: {"model": ErrorResponse, "description": "Not authenticated"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
    summary="Update user profile",
    description="Update profile details for the currently authenticated user.",
)
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    """Update and return the authenticated user's profile."""
    return await handle_update_profile(current_user, body, db)
