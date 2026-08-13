from pydantic import BaseModel, EmailStr, Field, field_validator


class PasswordRecoveryRequest(BaseModel):
    """Request body for initiating password recovery."""

    email: EmailStr = Field(
        ...,
        description=(
            "Registered email address associated with the account. "
            "A password reset link will be sent to this address."
        ),
        examples=["user@example.com"],
    )

    @field_validator("email")
    @classmethod
    def validate_email_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Email is required")
        return stripped


class PasswordRecoveryData(BaseModel):
    """Payload returned after a successful password recovery request."""

    email: EmailStr = Field(
        ...,
        description="Email address that received the password reset link",
        examples=["user@example.com"],
    )
    expires_in: int = Field(
        ...,
        description="Password reset link lifetime in seconds (30 minutes)",
        examples=[1800],
    )


class PasswordRecoveryResponse(BaseModel):
    """Success response for password recovery initiation."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Password recovery email sent successfully"],
    )
    data: PasswordRecoveryData
