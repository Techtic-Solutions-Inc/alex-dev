"""Shared API response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorBody(BaseModel):
    """Stable, frontend-safe details for a failed operation."""

    code: str = Field(
        description="Stable machine-readable error code.", examples=["VALIDATION_ERROR"]
    )
    details: Any | None = Field(
        default=None, description="Safe field-level or contextual error details."
    )


class ErrorResponse(BaseModel):
    """Standard error envelope returned by every API endpoint."""

    success: bool = Field(default=False, examples=[False])
    message: str = Field(description="Safe message suitable for display in the UI.")
    error: ErrorBody


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success envelope returned by every API endpoint."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(default=True, examples=[True])
    message: str = Field(description="Human-readable result message.")
    data: T
