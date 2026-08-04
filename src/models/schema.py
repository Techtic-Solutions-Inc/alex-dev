from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(
        description="Valid email address for the new account.",
        examples=["newuser@example.com"],
    )
    password: str = Field(
        min_length=8,
        description=(
            "Password with at least 8 characters, including uppercase, "
            "lowercase, digit, and special character."
        ),
        examples=["StrongPass1!"],
    )


class RegisterResponse(BaseModel):
    """Successful registration response."""

    email: EmailStr = Field(description="Registered email address.")
    message: str = Field(description="Human-readable status message.")


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(
        description="Registered email address.",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=1,
        description="Account password.",
    )


class LoginResponse(BaseModel):
    """Successful login response containing a JWT session token."""

    session_token: str = Field(description="JWT session token.")


class ConfirmEmailRequest(BaseModel):
    """Payload for POST /auth/confirm."""

    token: str = Field(
        min_length=1,
        description="Email confirmation token received via email.",
    )


class ConfirmEmailResponse(BaseModel):
    """Successful email confirmation response."""

    email: EmailStr = Field(description="Confirmed email address.")
    message: str = Field(description="Human-readable status message.")


class ProfileResponse(BaseModel):
    """User profile details returned by GET/PUT /api/profile."""

    id: int = Field(description="User ID.")
    first_name: str | None = Field(default=None, description="User's first name.")
    last_name: str | None = Field(default=None, description="User's last name.")
    email: EmailStr = Field(description="User's email address.")
    mobile_number: str | None = Field(
        default=None, description="User's mobile number."
    )
    bio: str | None = Field(default=None, description="Short biography.")
    address: str | None = Field(default=None, description="User's address.")
    profile_picture: str | None = Field(
        default=None, description="URL of the profile picture."
    )


class ProfileUpdateRequest(BaseModel):
    """Payload for PUT /api/profile."""

    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str | None = Field(
        default=None, max_length=100, description="User's first name."
    )
    last_name: str | None = Field(
        default=None, max_length=100, description="User's last name."
    )
    email: str | None = Field(default=None, description="User's email address.")
    mobile_number: str | None = Field(
        default=None, max_length=20, description="User's mobile number."
    )
    bio: str | None = Field(default=None, max_length=1000, description="Short biography.")
    address: str | None = Field(
        default=None, max_length=500, description="User's address."
    )
    profile_picture: str | None = Field(
        default=None, max_length=500, description="URL of the profile picture."
    )


class ErrorResponse(BaseModel):
    """Standard error envelope returned for all error responses."""

    detail: str = Field(description="Human-readable error description.")
