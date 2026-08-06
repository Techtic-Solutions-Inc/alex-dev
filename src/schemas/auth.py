"""Authentication request and response schemas."""

from pydantic import BaseModel, Field, field_validator

from src.utils.validation import PASSWORD_MIN_LENGTH, PASSWORD_PATTERN, normalize_email


class LoginRequest(BaseModel):
    """Credentials for user login."""

    email: str = Field(
        ...,
        min_length=1,
        description="Email address used to sign in.",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description="Account password. Must be at least 8 characters.",
        examples=["StrongPassword123!"],
    )
    remember_me: bool = Field(
        default=False,
        description=(
            "When true, extends the session lifetime so the user stays signed in "
            "on this device."
        ),
        examples=[False],
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Ensure the email address has a valid format."""
        return normalize_email(value)


class LoginResponseData(BaseModel):
    """User session data returned after a successful sign-in."""

    id: str = Field(..., description="Unique identifier for the authenticated user.")
    email: str = Field(..., description="Authenticated email address.")
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")
    expires_in: int = Field(..., description="Token lifetime in seconds.")
    title: str = Field(
        ...,
        description="Short headline for the sign-in success state.",
        examples=["Welcome back"],
    )
    message: str = Field(
        ...,
        description="User-facing sign-in confirmation message.",
        examples=["You have signed in successfully."],
    )
    description: str = Field(
        ...,
        description="Additional guidance shown after successful sign-in.",
        examples=["Everything you need to create standout real estate content."],
    )
    link: str | None = Field(
        default=None,
        description="Optional navigation link for the authenticated session.",
        examples=["/dashboard"],
    )


class LoginSuccessResponse(BaseModel):
    """Successful login response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Signed in successfully."],
    )
    data: LoginResponseData


class ValidateSessionResponseData(BaseModel):
    """Session validation data returned to the frontend."""

    id: str = Field(..., description="Unique identifier for the authenticated user.")
    email: str = Field(..., description="Authenticated email address.")
    title: str = Field(
        ...,
        description="Short headline for the active session state.",
        examples=["Session active"],
    )
    message: str = Field(
        ...,
        description="User-facing session validation message.",
        examples=["Your session is active."],
    )
    description: str = Field(
        ...,
        description="Additional guidance for the authenticated session.",
        examples=["You are signed in to Agentwise."],
    )
    link: str | None = Field(
        default=None,
        description="Optional navigation link for the authenticated session.",
        examples=["/dashboard"],
    )


class ValidateSessionSuccessResponse(BaseModel):
    """Successful session validation response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(..., examples=["Session is valid."])
    data: ValidateSessionResponseData


class SignupRequest(BaseModel):
    """Payload for registering a new user account."""

    email: str = Field(
        ...,
        min_length=1,
        description="Email address for the new account.",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        description=(
            "Account password. Must be at least 8 characters and include an "
            "uppercase letter, a number, and a special character."
        ),
        examples=["StrongPassword123!"],
    )

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


class SignupResponseData(BaseModel):
    """User registration data returned to the frontend."""

    id: str = Field(..., description="Unique identifier for the created user.")
    email: str = Field(..., description="Registered email address.")
    title: str = Field(
        ...,
        description="Short headline for the success state.",
        examples=["Account created"],
    )
    message: str = Field(
        ...,
        description="User-facing confirmation message.",
        examples=["Please check your email to confirm your account."],
    )
    description: str = Field(
        ...,
        description="Additional guidance shown after successful registration.",
        examples=[
            "We sent a confirmation email to your inbox. "
            "Click the link in that email to activate your account."
        ],
    )
    link: str | None = Field(
        default=None,
        description="Email confirmation link when available in non-production flows.",
        examples=["http://localhost:8000/api/auth/confirm-email?token=abc123"],
    )


class SignupSuccessResponse(BaseModel):
    """Successful signup response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(
        ...,
        examples=["Account created successfully. Please confirm your email."],
    )
    data: SignupResponseData


class ConfirmEmailResponseData(BaseModel):
    """Email confirmation data returned to the frontend."""

    id: str = Field(..., description="Unique identifier for the confirmed user.")
    email: str = Field(..., description="Confirmed email address.")
    title: str = Field(
        ...,
        description="Short headline for the confirmation success state.",
        examples=["Email confirmed"],
    )
    message: str = Field(
        ...,
        description="User-facing confirmation message.",
        examples=["Your email address has been verified."],
    )
    description: str = Field(
        ...,
        description="Additional guidance after email confirmation.",
        examples=["You can now sign in to your account."],
    )
    link: str = Field(
        ...,
        description="Link to the sign-in screen.",
        examples=["/sign-in"],
    )


class ConfirmEmailSuccessResponse(BaseModel):
    """Successful email confirmation response envelope."""

    success: bool = Field(default=True, examples=[True])
    message: str = Field(..., examples=["Email confirmed successfully."])
    data: ConfirmEmailResponseData
