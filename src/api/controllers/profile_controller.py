from sqlalchemy.ext.asyncio import AsyncSession

from api.validators.profile import validate_profile_update
from models.schema import ProfileResponse, ProfileUpdateRequest
from models.user import User
from services.profile import get_user_profile, update_user_profile


async def handle_get_profile(user: User) -> ProfileResponse:
    """Handle GET /api/profile request."""
    return await get_user_profile(user)


async def handle_update_profile(
    user: User,
    body: ProfileUpdateRequest,
    db: AsyncSession,
) -> ProfileResponse:
    """Handle PUT /api/profile request."""
    validate_profile_update(body)
    return await update_user_profile(user, body, db)
