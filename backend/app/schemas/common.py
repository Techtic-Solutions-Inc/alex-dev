"""Reusable API response envelopes."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Machine-readable error information that is safe for UI display."""

    code: str = Field(
        description="Stable machine-readable error code.",
        examples=["VALIDATION_ERROR"],
    )
    details: Any | None = Field(
        default=None,
        description="Field-level validation details when available; otherwise null.",
        examples=[{"email": ["Input should be a valid email address."]}],
    )


class ErrorResponse(BaseModel):
    """Standard error response emitted by all API error handlers."""

    success: bool = Field(default=False, description="Always false for an error response.")
    message: str = Field(description="UI-safe description of the error.")
    error: ErrorDetail = Field(description="Stable code and optional error details.")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard successful response envelope."""

    success: bool = Field(default=True, description="Always true for a successful response.")
    message: str = Field(description="UI-safe success message.")
    data: DataT = Field(description="Endpoint-specific response data.")
