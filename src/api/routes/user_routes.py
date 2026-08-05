from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.user_service import get_users_summary
from config.database import get_db_session
from models.schema import UsersSummaryResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/summary",
    response_model=UsersSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user count summary",
    description=(
        "Return the total number of registered users and the count of active users."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not found"},
    }
)
async def get_users_summary(
    db: AsyncSession = Depends(get_db_session),
) -> UsersSummaryResponse:
    """Return the total number of registered users and the count of active users."""
    return await get_users_summary(db)
