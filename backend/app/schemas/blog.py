import re
import uuid
from typing import Self

from pydantic import BaseModel, EmailStr, Field, field_validator

_PHONE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,20}$")


def _validate_terms_accepted(value: bool) -> bool:
    if not value:
        raise ValueError(
            "You must accept the Terms of Use and Privacy Policy"
        )
    return value


def _validate_phone(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Phone number is required")
    if not _PHONE_PATTERN.match(stripped):
        raise ValueError("Invalid phone number format")
    return stripped


class BlogCreateRequest(BaseModel):
    """Request body for creating a new blog post."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Blog post title",
        examples=["Hates to see me coming"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description=(
            "Full blog post content displayed on the Blog Details screen"
        ),
        examples=[
            "Lorem Ipsum has been the industry's standard dummy text ever since "
            "the 1500s, when an unknown printer took a galley of type and "
            "scrambled it to make a type specimen book."
        ],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Must be true to confirm acceptance of the Privacy Policy "
            "and Terms of Service"
        ),
        examples=[True],
    )
    phone: str = Field(
        ...,
        description="Contact phone number (Mobile App Development field)",
        examples=["+1-555-0100"],
    )
    first_name: str | None = Field(
        None,
        max_length=100,
        description="Contact first name from the user information form",
        examples=["Jane"],
    )
    last_name: str | None = Field(
        None,
        max_length=100,
        description="Contact last name from the user information form",
        examples=["Smith"],
    )
    email: EmailStr | None = Field(
        None,
        description="Contact email for blog inquiries",
        examples=["jane.smith@example.com"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description=(
            "Short summary of the blog post; auto-generated from content "
            "when omitted"
        ),
        examples=["A brief overview of the blog post content."],
    )

    @field_validator("title", "content")
    @classmethod
    def strip_and_validate_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_accepted(cls, value: bool) -> bool:
        return _validate_terms_accepted(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return _validate_phone(value)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_optional_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class BlogUpdateRequest(BaseModel):
    """Request body for updating an existing blog post."""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated blog post title",
        examples=["Updated blog title"],
    )
    content: str | None = Field(
        None,
        min_length=1,
        description="Updated blog post content",
        examples=["Updated blog content."],
    )
    terms_accepted: bool | None = Field(
        None,
        description=(
            "Must be true when provided; confirms acceptance of policies"
        ),
        examples=[True],
    )
    phone: str | None = Field(
        None,
        description="Updated contact phone number",
        examples=["+1-555-0199"],
    )
    first_name: str | None = Field(
        None,
        max_length=100,
        description="Updated contact first name",
        examples=["Jane"],
    )
    last_name: str | None = Field(
        None,
        max_length=100,
        description="Updated contact last name",
        examples=["Smith"],
    )
    email: EmailStr | None = Field(
        None,
        description="Updated contact email",
        examples=["jane.smith@example.com"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated short summary of the blog post",
        examples=["Updated summary."],
    )

    @field_validator("title", "content")
    @classmethod
    def strip_and_validate_optional_text(cls, value: str | None) -> str | None:
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

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_phone(value)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_optional_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class BlogData(BaseModel):
    """Blog post payload returned to the frontend."""

    id: str = Field(
        ...,
        description="Unique blog post identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    title: str = Field(
        ...,
        description="Blog post title",
        examples=["Hates to see me coming"],
    )
    content: str = Field(
        ...,
        description="Full blog post content",
        examples=["Lorem Ipsum has been the industry's standard dummy text..."],
    )
    description: str = Field(
        ...,
        description="Short summary or excerpt of the blog post",
        examples=["A brief overview of the blog post content."],
    )
    phone: str = Field(
        ...,
        description="Contact phone number",
        examples=["+1-555-0100"],
    )
    phone_number: str = Field(
        ...,
        description="Alias of phone for frontend compatibility",
        examples=["+1-555-0100"],
    )
    terms_accepted: bool = Field(
        ...,
        description="Whether terms and privacy policy were accepted",
        examples=[True],
    )
    first_name: str | None = Field(
        None,
        description="Contact first name",
        examples=["Jane"],
    )
    last_name: str | None = Field(
        None,
        description="Contact last name",
        examples=["Smith"],
    )
    email: str | None = Field(
        None,
        description="Contact email for inquiries",
        examples=["jane.smith@example.com"],
    )
    name: str = Field(
        ...,
        description="Full contact name derived from first and last name",
        examples=["Jane Smith"],
    )
    link: str = Field(
        ...,
        description="Relative URL to the blog post details endpoint",
        examples=["/api/blog/550e8400-e29b-41d4-a716-446655440000"],
    )
    error: str | None = Field(
        None,
        description=(
            "UI-facing error detail for the Blog Details screen; "
            "null on successful responses"
        ),
        examples=[None],
    )

    @classmethod
    def from_blog(cls, blog_id: uuid.UUID, **fields: object) -> Self:
        return cls(id=str(blog_id), **fields)  # type: ignore[arg-type]


class BlogResponse(BaseModel):
    """Success response for a single blog post."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Blog post retrieved successfully"],
    )
    data: BlogData


class BlogListData(BaseModel):
    """Paginated list of blog posts."""

    items: list[BlogData] = Field(
        ...,
        description="Blog posts matching the query",
    )
    total: int = Field(
        ...,
        description="Total number of blog posts available",
        examples=[1],
    )


class BlogListResponse(BaseModel):
    """Success response for listing blog posts."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Blog posts retrieved successfully"],
    )
    data: BlogListData
