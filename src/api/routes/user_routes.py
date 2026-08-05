from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.user_service import get_users_summary
from config.database import get_db_session
from models.schema import UsersSummaryResponse

router = APIRouter()


@router.get(
    "/summary",
    response_model=UsersSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user count summary",
    description=(
        "Return the total number of registered users and the count of active users."
    ),
)
async def users_summary(
    db: AsyncSession = Depends(get_db_session),
) -> UsersSummaryResponse:
    """Return total and active user counts."""
    return await get_users_summary(db)
