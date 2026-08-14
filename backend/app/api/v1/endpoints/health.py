from fastapi import APIRouter, Response, status

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
    tags=["Health"],
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Service is healthy",
                        "data": {"status": "healthy"},
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Internal server error",
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "details": None,
                        },
                    }
                }
            },
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


@router.options(
    "/health",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def health_check_options() -> Response:
    """Support CORS preflight probes on the health endpoint."""
    return Response(
        status_code=status.HTTP_200_OK,
        headers={"Access-Control-Allow-Origin": "*"},
    )
