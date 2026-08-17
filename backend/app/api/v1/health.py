"""Health check routes."""

from fastapi import APIRouter

from app.schemas.common import SuccessResponse
from app.schemas.health import HealthData, HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service health",
    description="Returns the health status of the service.",
)
async def health_check() -> SuccessResponse[HealthData]:
    return SuccessResponse(
        message="Service is operational.",
        data=HealthData(status="UP"),
    )
