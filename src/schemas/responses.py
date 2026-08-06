"""Standard API response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error payload returned to clients."""

    code: str = Field(..., description="Stable machine-readable error code.")
    details: Any | None = Field(
        default=None,
        description="Optional structured details such as field-level validation errors.",
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(default=False, examples=[False])
    message: str = Field(..., examples=["The request could not be processed."])
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(..., examples=["Operation completed successfully."])
    data: T


class ValidationErrorItem(BaseModel):
    """Single field validation error."""

    field: str = Field(..., examples=["username"])
    message: str = Field(..., examples=["Username is required"])


class ValidationErrorResponse(BaseModel):
    """Validation error response compatible with frontend forms."""

    detail: str = Field(default="Validation Error", examples=["Validation Error"])
    errors: list[ValidationErrorItem] = Field(default_factory=list)
