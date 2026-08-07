"""Email verification request and response schemas."""

from pydantic import BaseModel, Field, field_validator

from src.utils.validation import normalize_email


class EmailVerificationRequest(BaseModel):
    """Payload for requesting an email verification link."""

    email: str = Field(
        ...,
        min_length=1,
        description="Email address to verify (Verify Email Address field).",
        examples=["user@example.com"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Must be true to indicate acceptance of the Terms of Service and "
            "Privacy Policy before a verification email is sent."
        ),
        examples=[True],
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Ensure the email is present and has a valid format."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Email is required.")
        return normalize_email(value)


class EmailVerificationResponseData(BaseModel):
    """Data returned after a verification email is sent."""

    id: str = Field(..., description="Unique identifier for the user account.")
    email: str = Field(..., description="Email address the verification link was sent to.")
    first_name: str = Field(
        ...,
        description="User's first name for personalized UI messaging.",
        examples=["John"],
    )
    address: str = Field(
        ...,
        description="Verified email address displayed in the UI (same as email).",
        examples=["user@example.com"],
    )
    title: str = Field(
        ...,
        description="Short headline for the success state.",
        examples=["Verify your email address"],
    )
    message: str = Field(
        ...,
        description="User-facing confirmation message.",
        examples=["We sent a verification link to your email."],
    )
    description: str = Field(
        ...,
        description="Additional guidance about the verification link and expiry.",
        examples=[
            "This verification link will expire in 24 hours. If you didn't create "
            "an account on Agentwise, you can safely ignore this email."
        ],
    )
    link: str | None = Field(
        default=None,
        description=(
            "Email verification link when available in non-production flows for testing."
        ),
        examples=["http://localhost:8000/api/auth/confirm-email?token=abc123"],
    )


class EmailVerificationSuccessResponse(BaseModel):
    """Successful email verification request response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Verification email sent successfully."],
    )
    data: EmailVerificationResponseData
