from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Machine-readable error payload."""

    code: str = Field(
        ...,
        description="Stable machine-readable error code",
        examples=["VALIDATION_ERROR"],
    )
    details: Any = Field(
        None,
        description="Additional error details, such as field-level validation errors",
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(False, description="Indicates the request failed")
    message: str = Field(
        ...,
        description="UI-safe error message",
        examples=["Validation error"],
    )
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Operation completed successfully"],
    )
    data: T
