import uuid
from typing import Self

from pydantic import BaseModel, Field, field_validator


def _validate_consent_accepted(value: bool, field_label: str) -> bool:
    if not value:
        raise ValueError(f"You must accept the {field_label}")
    return value


class AnnouncementCreateRequest(BaseModel):
    """Request body for creating a new announcement."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Announcement title displayed on the Announcement screen",
        examples=["Announcement Title"],
    )
    body: str = Field(
        ...,
        min_length=1,
        description="Main announcement body text",
        examples=["Announcement body text"],
    )
    highlights: list[str] = Field(
        ...,
        min_length=1,
        description="Bullet highlights rendered on the Announcement screen",
        examples=[["Highlight 1", "Highlight 2", "Highlight 3"]],
    )
    privacy_policy_accepted: bool = Field(
        ...,
        description="Must be true to confirm acceptance of the Privacy Policy",
        examples=[True],
    )
    terms_of_service_accepted: bool = Field(
        ...,
        description="Must be true to confirm acceptance of the Terms of Service",
        examples=[True],
    )

    @field_validator("title", "body")
    @classmethod
    def strip_and_validate_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped

    @field_validator("highlights")
    @classmethod
    def validate_highlights(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("At least one highlight is required")
        cleaned: list[str] = []
        for index, item in enumerate(value):
            stripped = item.strip()
            if not stripped:
                raise ValueError(f"Highlight at index {index} cannot be empty")
            cleaned.append(stripped)
        return cleaned

    @field_validator("privacy_policy_accepted")
    @classmethod
    def privacy_policy_must_be_accepted(cls, value: bool) -> bool:
        return _validate_consent_accepted(value, "Privacy Policy")

    @field_validator("terms_of_service_accepted")
    @classmethod
    def terms_of_service_must_be_accepted(cls, value: bool) -> bool:
        return _validate_consent_accepted(value, "Terms of Service")


class AnnouncementUpdateRequest(BaseModel):
    """Request body for updating an existing announcement."""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated announcement title",
        examples=["Updated Announcement Title"],
    )
    body: str | None = Field(
        None,
        min_length=1,
        description="Updated announcement body text",
        examples=["Updated announcement body text"],
    )
    highlights: list[str] | None = Field(
        None,
        min_length=1,
        description="Updated bullet highlights",
        examples=[["Updated highlight 1", "Updated highlight 2"]],
    )
    privacy_policy_accepted: bool | None = Field(
        None,
        description="Must be true when provided; confirms Privacy Policy acceptance",
        examples=[True],
    )
    terms_of_service_accepted: bool | None = Field(
        None,
        description="Must be true when provided; confirms Terms of Service acceptance",
        examples=[True],
    )

    @field_validator("title", "body")
    @classmethod
    def strip_and_validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field cannot be empty")
        return stripped

    @field_validator("highlights")
    @classmethod
    def validate_highlights(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if not value:
            raise ValueError("At least one highlight is required")
        cleaned: list[str] = []
        for index, item in enumerate(value):
            stripped = item.strip()
            if not stripped:
                raise ValueError(f"Highlight at index {index} cannot be empty")
            cleaned.append(stripped)
        return cleaned

    @field_validator("privacy_policy_accepted")
    @classmethod
    def privacy_policy_must_be_accepted(cls, value: bool | None) -> bool | None:
        if value is None:
            return None
        return _validate_consent_accepted(value, "Privacy Policy")

    @field_validator("terms_of_service_accepted")
    @classmethod
    def terms_of_service_must_be_accepted(cls, value: bool | None) -> bool | None:
        if value is None:
            return None
        return _validate_consent_accepted(value, "Terms of Service")


class AnnouncementData(BaseModel):
    """Announcement payload returned to the frontend."""

    id: str = Field(
        ...,
        description="Unique announcement identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    title: str = Field(
        ...,
        description="Announcement title",
        examples=["Announcement Title"],
    )
    body: str = Field(
        ...,
        description="Announcement body text",
        examples=["Announcement body text"],
    )
    highlights: list[str] = Field(
        ...,
        description="Bullet highlights for the announcement",
        examples=[["Highlight 1", "Highlight 2", "Highlight 3"]],
    )
    privacy_policy_accepted: bool = Field(
        ...,
        description="Whether the Privacy Policy was accepted",
        examples=[True],
    )
    terms_of_service_accepted: bool = Field(
        ...,
        description="Whether the Terms of Service were accepted",
        examples=[True],
    )

    @classmethod
    def from_announcement(cls, announcement_id: uuid.UUID, **fields: object) -> Self:
        return cls(id=str(announcement_id), **fields)  # type: ignore[arg-type]


class AnnouncementResponse(BaseModel):
    """Success response for a single announcement."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Announcement retrieved successfully"],
    )
    data: AnnouncementData


class AnnouncementListData(BaseModel):
    """Paginated list of announcements."""

    items: list[AnnouncementData] = Field(
        ...,
        description="Announcements matching the query",
    )
    total: int = Field(
        ...,
        description="Total number of announcements matching the query",
        examples=[1],
    )
    page: int = Field(
        ...,
        description="Current page number (1-based)",
        examples=[1],
    )
    limit: int = Field(
        ...,
        description="Maximum number of announcements returned per page",
        examples=[20],
    )


class AnnouncementListResponse(BaseModel):
    """Success response for listing announcements."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Announcements retrieved successfully"],
    )
    data: AnnouncementListData
