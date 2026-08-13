import re
import uuid
from typing import Self

from pydantic import BaseModel, EmailStr, Field, field_validator

_PHONE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,20}$")
_SQL_INJECTION_PATTERN = re.compile(
    r"(?i)"
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|EXEC|EXECUTE)\b"
    r"|--|;|/\*|\*/|'|\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)"
)


def _validate_consent_accepted(value: bool, field_label: str) -> bool:
    if not value:
        raise ValueError(f"You must accept the {field_label}")
    return value


def _validate_phone_number(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Phone number is required")
    if not _PHONE_PATTERN.match(stripped):
        raise ValueError("Invalid phone number format")
    return stripped


def _validate_no_sql_injection(value: str, field_name: str) -> str:
    if _SQL_INJECTION_PATTERN.search(value):
        raise ValueError(f"Invalid characters detected in {field_name}")
    return value


def _strip_required_text(value: str, field_label: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_label} is required")
    return stripped


class BlogDetailsSubmitRequest(BaseModel):
    """Request body for submitting blog details contact information."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact first name from the Blog Details form",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact last name from the Blog Details form",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Contact email address",
        examples=["john.doe@example.com"],
    )
    phone_number: str = Field(
        ...,
        description="Contact phone number",
        examples=["1234567890"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message submitted on the Blog Details screen",
        examples=["This is a sample message."],
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

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, value: str) -> str:
        stripped = _strip_required_text(value, "This field")
        return _validate_no_sql_injection(stripped, "name")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        stripped = _strip_required_text(value, "Message")
        return _validate_no_sql_injection(stripped, "message")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        validated = _validate_phone_number(value)
        return _validate_no_sql_injection(validated, "phone_number")

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_input(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Email is required")
            return _validate_no_sql_injection(stripped, "email")
        return value

    @field_validator("privacy_policy_accepted")
    @classmethod
    def privacy_policy_must_be_accepted(cls, value: bool) -> bool:
        return _validate_consent_accepted(value, "Privacy Policy")

    @field_validator("terms_of_service_accepted")
    @classmethod
    def terms_of_service_must_be_accepted(cls, value: bool) -> bool:
        return _validate_consent_accepted(value, "Terms of Service")


class BlogDetailsUpdateRequest(BaseModel):
    """Request body for updating an existing blog details submission."""

    first_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated contact first name",
        examples=["John"],
    )
    last_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated contact last name",
        examples=["Doe"],
    )
    email: EmailStr | None = Field(
        None,
        description="Updated contact email address",
        examples=["john.doe@example.com"],
    )
    phone_number: str | None = Field(
        None,
        description="Updated contact phone number",
        examples=["1234567890"],
    )
    message: str | None = Field(
        None,
        min_length=1,
        max_length=5000,
        description="Updated user message",
        examples=["Updated message text."],
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

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_optional_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = _strip_required_text(value, "This field")
        return _validate_no_sql_injection(stripped, "name")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = _strip_required_text(value, "Message")
        return _validate_no_sql_injection(stripped, "message")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        validated = _validate_phone_number(value)
        return _validate_no_sql_injection(validated, "phone_number")

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_input(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Email cannot be empty")
            return _validate_no_sql_injection(stripped, "email")
        return value

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


class BlogDetailsHeading(BaseModel):
    """A heading displayed on the Blog Details screen."""

    id: str = Field(
        ...,
        description="Stable identifier for the heading",
        examples=["main-title"],
    )
    text: str = Field(
        ...,
        description="Heading text",
        examples=["Hates to see me coming"],
    )
    level: int = Field(
        ...,
        ge=1,
        le=6,
        description="HTML heading level (1–6)",
        examples=[1],
    )


class BlogDetailsSection(BaseModel):
    """A content section with heading and body text."""

    heading: str = Field(
        ...,
        description="Section heading",
        examples=["Overview"],
    )
    text: str = Field(
        ...,
        description="Section body text",
        examples=["Learn more about our latest blog post."],
    )


class BlogDetailsPageContent(BaseModel):
    """Blog Details screen page content returned on GET."""

    headings: list[BlogDetailsHeading] = Field(
        ...,
        description="Ordered headings for the Blog Details screen",
    )
    content: str = Field(
        ...,
        description="Primary blog body text",
        examples=[
            "Lorem Ipsum has been the industry's standard dummy text ever since "
            "the 1500s, when an unknown printer took a galley of type and "
            "scrambled it to make a type specimen book."
        ],
    )
    sections: list[BlogDetailsSection] = Field(
        ...,
        description="Additional content sections with headings and text",
    )
    additional_info: str = Field(
        ...,
        description="Supplementary information shown on the Blog Details screen",
        examples=[
            "Fill out the form below to get in touch about this blog post."
        ],
    )


class BlogDetailsSubmissionData(BaseModel):
    """A stored blog details contact form submission."""

    id: str = Field(
        ...,
        description="Unique submission identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str = Field(
        ...,
        description="Contact first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        description="Contact last name",
        examples=["Doe"],
    )
    email: str = Field(
        ...,
        description="Contact email address",
        examples=["john.doe@example.com"],
    )
    phone_number: str = Field(
        ...,
        description="Contact phone number",
        examples=["1234567890"],
    )
    message: str = Field(
        ...,
        description="User message",
        examples=["This is a sample message."],
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
    def from_submission(cls, submission_id: uuid.UUID, **fields: object) -> Self:
        return cls(id=str(submission_id), **fields)  # type: ignore[arg-type]


class BlogDetailsGetData(BaseModel):
    """Payload returned when retrieving Blog Details page content."""

    page: BlogDetailsPageContent = Field(
        ...,
        description="Blog content, headings, and sections for the Blog Details screen",
    )
    link: str = Field(
        ...,
        description="Relative URL to the Blog Details endpoint",
        examples=["/api/blog/details"],
    )


class BlogDetailsGetResponse(BaseModel):
    """Success response for retrieving Blog Details page content."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Blog details retrieved successfully"],
    )
    data: BlogDetailsGetData


class BlogDetailsSubmissionResponse(BaseModel):
    """Success response for blog details submission operations."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Blog details submitted successfully"],
    )
    data: BlogDetailsSubmissionData
