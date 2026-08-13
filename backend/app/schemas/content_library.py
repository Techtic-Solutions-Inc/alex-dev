from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.user import User
from app.schemas.common import SuccessResponse

ContentTemplateStatus = Literal["active", "inactive"]


class UserDetailsData(BaseModel):
    """Logged-in user details for the Content Library screen."""

    user_id: str = Field(
        ...,
        description="Authenticated user's UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="Display name (first name and last name)",
        examples=["John Doe"],
    )
    ai_credit_usage: int = Field(
        ...,
        ge=0,
        description="Current AI credit usage count for the authenticated user",
        examples=[42],
    )

    @classmethod
    def from_user(cls, user: User) -> "UserDetailsData":
        """Build response data from a User ORM instance."""
        name = f"{user.first_name} {user.last_name}".strip()
        return cls(
            user_id=str(user.id),
            name=name,
            ai_credit_usage=int(user.ai_credit_usage or 0),
        )


class UserDetailsResponse(SuccessResponse[UserDetailsData]):
    """Success envelope for Content Library user details."""

    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["User details retrieved successfully"],
    )
    data: UserDetailsData


class ContentTemplateCreateRequest(BaseModel):
    """Request body for creating a new content template."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Template title displayed in the Content Library",
        examples=["Open House Flyer"],
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="Optional template description or summary",
        examples=["A professional open house marketing template"],
    )
    status: ContentTemplateStatus = Field(
        default="active",
        description="Template visibility status (`active` or `inactive`)",
        examples=["active"],
    )

    @field_validator("title")
    @classmethod
    def strip_and_validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title is required")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_optional_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ContentTemplateUpdateRequest(BaseModel):
    """Request body for updating an existing content template."""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated template title",
        examples=["Updated Open House Flyer"],
    )
    description: str | None = Field(
        None,
        max_length=5000,
        description="Updated template description",
        examples=["Updated marketing template description"],
    )
    status: ContentTemplateStatus | None = Field(
        None,
        description="Updated template status (`active` or `inactive`)",
        examples=["inactive"],
    )

    @field_validator("title")
    @classmethod
    def strip_and_validate_optional_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_optional_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ContentTemplateData(BaseModel):
    """Content template payload returned to the frontend."""

    id: str = Field(
        ...,
        description="Unique content template identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    title: str = Field(
        ...,
        description="Template title",
        examples=["Open House Flyer"],
    )
    description: str | None = Field(
        None,
        description="Template description",
        examples=["A professional open house marketing template"],
    )
    status: ContentTemplateStatus = Field(
        ...,
        description="Template status (`active` or `inactive`)",
        examples=["active"],
    )


class ContentTemplateResponse(BaseModel):
    """Success response for a single content template."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Content template retrieved successfully"],
    )
    data: ContentTemplateData


class ContentTemplateListData(BaseModel):
    """Paginated list of content templates."""

    items: list[ContentTemplateData] = Field(
        ...,
        description="Content templates matching the query",
    )
    total: int = Field(
        ...,
        description="Total number of templates matching the query",
        examples=[1],
    )
    page: int = Field(
        ...,
        description="Current page number (1-based)",
        examples=[1],
    )
    limit: int = Field(
        ...,
        description="Maximum number of templates returned per page",
        examples=[20],
    )


class ContentTemplateListResponse(BaseModel):
    """Success response for listing or searching content templates."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Content templates retrieved successfully"],
    )
    data: ContentTemplateListData
