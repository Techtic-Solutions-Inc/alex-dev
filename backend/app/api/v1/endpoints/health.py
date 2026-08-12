from fastapi import APIRouter, status

from app.schemas.common import ErrorResponse
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description=(
        "Returns the current health status of the API service. "
        "Use this endpoint for load balancer health probes and uptime monitoring. "
        "No authentication is required."
    ),
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
async def health_check() -> HealthResponse:
    """Verify that the API service is running and responsive."""
    return HealthResponse(
        success=True,
        message="Service is healthy",
        data={"status": "healthy"},
    )
