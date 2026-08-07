"""User request and response schemas."""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


class UserBase(BaseModel):
    """Shared user fields with validation rules."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username containing letters, numbers, or underscores.",
        examples=["jane_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address for the user account.",
        examples=["jane@example.com"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Ensure username matches allowed pattern."""
        if not USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username may only contain letters, numbers, and underscores."
            )
        return value


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        description="Plain-text password; must be at least 8 characters.",
        examples=["securePass123"],
    )


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Updated username.",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Updated email address.",
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        description="Updated password.",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        """Ensure username matches allowed pattern when provided."""
        if value is not None and not USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username may only contain letters, numbers, and underscores."
            )
        return value


class UserResponse(UserBase):
    """Public user representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique user identifier.")
    created_at: datetime = Field(..., description="Timestamp when the user was created.")
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of the most recent user update.",
    )
