"""Public health-check endpoint."""

from fastapi import APIRouter, status

from app.schemas.common import ErrorResponse
from app.schemas.health import HealthData, HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check API health",
    description=(
        "Reports whether the API process is available. This endpoint is public and is intended "
        "for load balancers, uptime monitors, and deployment checks."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Malformed request."},
        401: {"model": ErrorResponse, "description": "Authentication is required."},
        403: {"model": ErrorResponse, "description": "Access is forbidden."},
        404: {"model": ErrorResponse, "description": "Health resource was not found."},
        409: {"model": ErrorResponse, "description": "Service state conflict."},
        422: {"model": ErrorResponse, "description": "Validation failed."},
        500: {"model": ErrorResponse, "description": "Unexpected server error."},
    },
)
async def health_check() -> HealthResponse:
    """Return the public availability state without exposing infrastructure details."""
    return HealthResponse(message="Service is operational.", data=HealthData(status="UP"))
