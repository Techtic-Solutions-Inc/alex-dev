"""Health check routes."""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str = Field(
        ...,
        description="Current service health status.",
        examples=["healthy"],
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description=(
        "Returns the current health status of the API. Use this endpoint for "
        "load balancer probes and uptime monitoring. No authentication is required."
    ),
    responses={
        200: {
            "description": "Service is healthy and accepting requests.",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"},
                }
            },
        },
        429: {
            "description": "Rate limit exceeded.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Rate limit exceeded. Please try again later.",
                        "error": {"code": "RATE_LIMIT_EXCEEDED", "details": None},
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal Server Error",
                        "success": False,
                        "message": "Internal Server Error",
                        "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                    }
                }
            },
        },
    },
    tags=["Health"],
)
async def health_check() -> dict[str, Any]:
    """Verify that the API is running and responsive."""
    return {"status": "healthy"}
