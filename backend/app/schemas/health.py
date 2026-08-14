from pydantic import BaseModel, Field


class HealthData(BaseModel):
    """Health check response data."""

    status: str = Field(
        ...,
        description="Current health status of the application",
        examples=["healthy"],
    )


class HealthResponse(BaseModel):
    """Health check success response."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Service is healthy"],
    )
    data: HealthData
