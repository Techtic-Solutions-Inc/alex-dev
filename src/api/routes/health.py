"""Health check routes."""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.schemas.responses import ErrorDetail

router = APIRouter()


class HealthData(BaseModel):
    """Frontend-compatible health payload used by boot and integration checks."""

    id: str = Field(
        default="system",
        description="Stable identifier for the health check response.",
        examples=["system"],
    )
    email: str = Field(
        default="health@system.local",
        description="Placeholder email for frontend contract validation.",
        examples=["health@system.local"],
    )
    title: str = Field(
        default="Service healthy",
        description="Short headline for the health state.",
        examples=["Service healthy"],
    )
    message: str = Field(
        default="All systems operational.",
        description="User-facing health confirmation message.",
        examples=["All systems operational."],
    )
    description: str = Field(
        default="Backend API is running and accepting requests.",
        description="Additional guidance for monitoring and frontend integration.",
        examples=["Backend API is running and accepting requests."],
    )
    link: str = Field(
        default="/docs",
        description="Link to API documentation.",
        examples=["/docs"],
    )


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str = Field(
        ...,
        description="Current service health status.",
        examples=["healthy"],
    )
    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        default="API is operational.",
        description="Top-level health message.",
        examples=["API is operational."],
    )
    error: ErrorDetail | None = Field(
        default=None,
        description="Null on successful health checks.",
    )
    data: HealthData


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
                    "example": {
                        "status": "healthy",
                        "success": True,
                        "message": "API is operational.",
                        "error": None,
                        "data": {
                            "id": "system",
                            "email": "health@system.local",
                            "title": "Service healthy",
                            "message": "All systems operational.",
                            "description": (
                                "Backend API is running and accepting requests."
                            ),
                            "link": "/docs",
                        },
                    },
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
    return {
        "status": "healthy",
        "success": True,
        "message": "API is operational.",
        "error": None,
        "data": {
            "id": "system",
            "email": "health@system.local",
            "title": "Service healthy",
            "message": "All systems operational.",
            "description": "Backend API is running and accepting requests.",
            "link": "/docs",
        },
    }
