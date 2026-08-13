import re
import uuid
from typing import Self

from pydantic import BaseModel, Field, field_validator

_PHONE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,20}$")


def _validate_terms_accepted(value: bool) -> bool:
    if not value:
        raise ValueError(
            "You must accept the Terms of Use and Privacy Policy"
        )
    return value


def _validate_privacy_policy(value: bool) -> bool:
    if not value:
        raise ValueError("You must accept the Privacy Policy")
    return value


def _validate_phone(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Phone number is required")
    if not _PHONE_PATTERN.match(stripped):
        raise ValueError("Invalid phone number format")
    return stripped


class ContentCreateRequest(BaseModel):
    """Request body for creating content details (Content Details form)."""

    caption: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Content caption displayed on the Content Details screen",
        examples=["Hates to see me coming"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Privacy Policy / Terms checkbox; must be true to confirm acceptance"
        ),
        examples=[True],
    )
    privacy_policy: bool = Field(
        ...,
        description="Privacy Policy acceptance checkbox; must be true",
        examples=[True],
    )
    phone: str = Field(
        ...,
        description="Contact phone number (Mobile App Development field)",
        examples=["+1-555-0100"],
    )
    full_name: str | None = Field(
        None,
        max_length=200,
        description="Display name shown on the Content Calendar (e.g. Joseph)",
        examples=["Joseph"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description=(
            "Short summary of the content; auto-generated from caption when omitted"
        ),
        examples=["Your personal content calendar designed to grow your business"],
    )

    @field_validator("caption")
    @classmethod
    def strip_and_validate_caption(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_accepted(cls, value: bool) -> bool:
        return _validate_terms_accepted(value)

    @field_validator("privacy_policy")
    @classmethod
    def privacy_must_be_accepted(cls, value: bool) -> bool:
        return _validate_privacy_policy(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return _validate_phone(value)

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ContentUpdateRequest(BaseModel):
    """Request body for updating existing content details."""

    caption: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated content caption",
        examples=["Updated caption"],
    )
    terms_accepted: bool | None = Field(
        None,
        description="Must be true when provided; confirms policy acceptance",
        examples=[True],
    )
    privacy_policy: bool | None = Field(
        None,
        description="Must be true when provided; confirms Privacy Policy acceptance",
        examples=[True],
    )
    phone: str | None = Field(
        None,
        description="Updated contact phone number",
        examples=["+1-555-0199"],
    )
    full_name: str | None = Field(
        None,
        max_length=200,
        description="Updated display name for the Content Calendar",
        examples=["Joseph"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated short summary of the content",
        examples=["Updated content summary."],
    )

    @field_validator("caption")
    @classmethod
    def strip_and_validate_caption(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field cannot be empty")
        return stripped

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_accepted(cls, value: bool | None) -> bool | None:
        if value is None:
            return None
        return _validate_terms_accepted(value)

    @field_validator("privacy_policy")
    @classmethod
    def privacy_must_be_accepted(cls, value: bool | None) -> bool | None:
        if value is None:
            return None
        return _validate_privacy_policy(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_phone(value)

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ContentData(BaseModel):
    """Content details payload returned to the frontend."""

    id: str = Field(
        ...,
        description="Unique content identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    caption: str = Field(
        ...,
        description="Content caption",
        examples=["Hates to see me coming"],
    )
    description: str = Field(
        ...,
        description="Short summary used by the Content Calendar screen",
        examples=["Your personal content calendar designed to grow your business"],
    )
    phone: str = Field(
        ...,
        description="Contact phone number (Mobile App Development)",
        examples=["+1-555-0100"],
    )
    terms_accepted: bool = Field(
        ...,
        description="Whether terms / privacy policy were accepted",
        examples=[True],
    )
    privacy_policy: bool = Field(
        ...,
        description="Whether the Privacy Policy checkbox was accepted",
        examples=[True],
    )
    full_name: str | None = Field(
        None,
        description="Display name for the Content Calendar heading",
        examples=["Joseph"],
    )
    link: str = Field(
        ...,
        description="Relative URL to the content details endpoint",
        examples=["/api/content/550e8400-e29b-41d4-a716-446655440000"],
    )
    error: str | None = Field(
        None,
        description=(
            "UI-facing error detail for content screens; null on successful responses"
        ),
        examples=[None],
    )

    @classmethod
    def from_content(cls, content_id: uuid.UUID, **fields: object) -> Self:
        return cls(id=str(content_id), **fields)  # type: ignore[arg-type]


class ContentResponse(BaseModel):
    """Success response for a single content record."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Content retrieved successfully"],
    )
    data: ContentData
