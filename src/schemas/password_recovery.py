"""Password recovery request and response schemas."""

from pydantic import BaseModel, Field, field_validator

from src.utils.validation import PASSWORD_MIN_LENGTH, PASSWORD_PATTERN, normalize_email


class PasswordRecoveryRequest(BaseModel):
    """Payload for requesting a password reset link."""

    email: str = Field(
        ...,
        min_length=1,
        description="Email address associated with the account.",
        examples=["user@example.com"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Must be true to indicate acceptance of the Terms of Service and "
            "Privacy Policy before a reset link is sent."
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


class PasswordResetRequest(BaseModel):
    """Payload for resetting a password using a valid reset token."""

    token: str = Field(
        ...,
        min_length=1,
        description="Password reset token from the reset email link.",
        examples=["abc123def456"],
    )
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description=(
            "New account password (Reset My Password field). Must be at least 8 "
            "characters and include an uppercase letter, a number, and a special "
            "character."
        ),
        examples=["StrongPassword123!"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Must be true to indicate acceptance of the Terms of Service and "
            "Privacy Policy before the password is updated."
        ),
        examples=[True],
    )

    @field_validator("token")
    @classmethod
    def validate_token(cls, value: str) -> str:
        """Ensure the reset token is present."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("A password reset token is required.")
        return stripped

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Ensure password meets strength requirements."""
        if len(value) < PASSWORD_MIN_LENGTH:
            raise ValueError(
                "Password must be at least 8 characters long and include an uppercase "
                "letter, a number, and a special character."
            )
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be at least 8 characters long and include an uppercase "
                "letter, a number, and a special character."
            )
        return value


class PasswordRecoveryResponseData(BaseModel):
    """Data returned after a password reset link is requested."""

    id: str = Field(..., description="Unique identifier for the user account.")
    email: str = Field(..., description="Email address the reset link was sent to.")
    title: str = Field(
        ...,
        description="Short headline for the success state.",
        examples=["Check your email"],
    )
    message: str = Field(
        ...,
        description="User-facing confirmation message.",
        examples=["We sent a password reset link to your email."],
    )
    description: str = Field(
        ...,
        description="Additional guidance about the reset link and expiry.",
        examples=[
            "The link is valid for 30 minutes. If you did not request a reset, "
            "you can safely ignore this email."
        ],
    )
    link: str | None = Field(
        default=None,
        description=(
            "Password reset link when available in non-production flows for testing."
        ),
        examples=["http://localhost:8000/api/password-recovery/validate/abc123"],
    )


class PasswordRecoverySuccessResponse(BaseModel):
    """Successful password recovery request response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Password reset link sent successfully."],
    )
    data: PasswordRecoveryResponseData


class ValidateResetTokenResponseData(BaseModel):
    """Data returned when a password reset token is valid."""

    id: str = Field(..., description="Unique identifier for the user account.")
    email: str = Field(..., description="Email address associated with the token.")
    title: str = Field(
        ...,
        description="Short headline for the valid token state.",
        examples=["Reset your password"],
    )
    message: str = Field(
        ...,
        description="User-facing token validation message.",
        examples=["Your reset link is valid."],
    )
    description: str = Field(
        ...,
        description="Additional guidance for setting a new password.",
        examples=["Enter a new password below to complete the reset."],
    )
    link: str | None = Field(
        default=None,
        description="Frontend route for completing the password reset.",
        examples=["/reset-password"],
    )


class ValidateResetTokenSuccessResponse(BaseModel):
    """Successful password reset token validation response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Password reset token is valid."],
    )
    data: ValidateResetTokenResponseData


class PasswordResetResponseData(BaseModel):
    """Data returned after a password is successfully reset."""

    id: str = Field(..., description="Unique identifier for the user account.")
    email: str = Field(..., description="Email address for the updated account.")
    title: str = Field(
        ...,
        description="Short headline for the reset success state.",
        examples=["Password updated"],
    )
    message: str = Field(
        ...,
        description="User-facing password reset confirmation message.",
        examples=["Your password has been reset successfully."],
    )
    description: str = Field(
        ...,
        description="Additional guidance after a successful password reset.",
        examples=["You can now sign in with your new password."],
    )
    link: str = Field(
        ...,
        description="Link to the sign-in screen.",
        examples=["/sign-in"],
    )


class PasswordResetSuccessResponse(BaseModel):
    """Successful password reset response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Password reset successfully."],
    )
    data: PasswordResetResponseData
