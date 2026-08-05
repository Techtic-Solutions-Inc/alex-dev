"""User-related API service functions."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.schema import UsersSummaryResponse
from models.user import User


async def get_users_summary(db: AsyncSession) -> UsersSummaryResponse:
    """Return total and active user counts from the users table."""
    total_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_result.scalar_one()

    active_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    active_users = active_result.scalar_one()

    return UsersSummaryResponse(
        total_users=total_users,
        active_users=active_users,
    )
