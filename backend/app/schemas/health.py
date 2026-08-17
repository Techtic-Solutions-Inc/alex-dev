"""Health check response schemas."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import SuccessResponse


class HealthData(BaseModel):
    """Service health status."""

    status: Literal["UP"] = Field(
        description="Service availability status.",
        examples=["UP"],
    )


HealthResponse = SuccessResponse[HealthData]
