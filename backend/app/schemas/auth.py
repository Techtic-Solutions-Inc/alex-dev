"""Typed request and response contracts for authentication endpoints."""

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """Registration form submitted by a new user."""

    first_name: str = Field(
        min_length=1, max_length=100, description="User's given name.", examples=["Ada"]
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's family name.",
        examples=["Lovelace"],
    )
    email: EmailStr = Field(
        description="Unique email address used to sign in.",
        examples=["ada@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password with uppercase, lowercase, number, and symbol.",
        examples=["S3cure!Pass"],
    )
    terms_accepted: bool = Field(
        description="Must be true to confirm acceptance of the terms.", examples=[True]
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def non_blank_name(cls, value: str) -> str:
        """Reject whitespace-only names and normalize surrounding whitespace."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field is required.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Enforce a baseline password policy without retaining the password."""
        if not (
            any(char.islower() for char in value)
            and any(char.isupper() for char in value)
            and any(char.isdigit() for char in value)
            and any(not char.isalnum() for char in value)
        ):
            raise ValueError(
                "Password must contain uppercase, lowercase, number, and symbol."
            )
        return value

    @field_validator("terms_accepted")
    @classmethod
    def require_terms_acceptance(cls, value: bool) -> bool:
        """Require an explicit acceptance before account creation."""
        if not value:
            raise ValueError("Terms must be accepted.")
        return value


class LoginRequest(BaseModel):
    """Credentials submitted to create a session."""

    email: EmailStr = Field(
        description="Registered email address.", examples=["ada@example.com"]
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description=(
            "Account password. It must contain at least one uppercase letter, one "
            "lowercase letter, and one number."
        ),
        examples=["S3cure!Pass"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Reject login form passwords that violate the documented security policy."""
        if not (
            any(char.islower() for char in value)
            and any(char.isupper() for char in value)
            and any(char.isdigit() for char in value)
        ):
            raise ValueError(
                "Password must contain an uppercase letter, lowercase letter, and number."
            )
        return value


class RefreshRequest(BaseModel):
    """Refresh token submitted to rotate a session."""

    refresh_token: str = Field(
        min_length=1,
        description="Valid refresh token returned by login or a previous refresh.",
        examples=["eyJhbGciOiJIUzI1NiIs..."],
    )


class UserData(BaseModel):
    """Safe user information returned to the client."""

    id: str = Field(description="Public user UUID.", examples=["7a95c2ce-2d3d-4ff4-8d27-6f40ecae6efa"])
    first_name: str = Field(description="User's given name.", examples=["Ada"])
    last_name: str = Field(description="User's family name.", examples=["Lovelace"])
    email: EmailStr = Field(description="User's email address.", examples=["ada@example.com"])
    email_verified: bool = Field(
        description="Whether the user has confirmed ownership of this email address.",
        examples=[False],
    )


class EmailVerificationData(BaseModel):
    """Safe result returned after an email verification link is used."""

    id: str = Field(description="Public user UUID.", examples=["7a95c2ce-2d3d-4ff4-8d27-6f40ecae6efa"])
    email: EmailStr = Field(description="Verified email address.", examples=["ada@example.com"])
    email_verified: bool = Field(
        description="Confirmation state after processing the verification link.",
        examples=[True],
    )
    name: str = Field(description="User's display name.", examples=["Ada Lovelace"])


class TokenData(BaseModel):
    """JWT credentials returned after authentication."""

    access_token: str = Field(description="Short-lived bearer access token.")
    token: str = Field(
        description=(
            "Alias of access_token retained for clients that use the Sign In form "
            "contract."
        )
    )
    refresh_token: str = Field(description="Single-use rotating refresh token.")
    token_type: str = Field(default="bearer", description="Authorization scheme.", examples=["bearer"])
    expires_in: int = Field(description="Access token lifetime in seconds.", examples=[3600])
    user: UserData


class SignupData(TokenData):
    """Registration result with direct access to frontend profile fields."""

    id: str = Field(description="Public user UUID.", examples=["7a95c2ce-2d3d-4ff4-8d27-6f40ecae6efa"])
    first_name: str = Field(description="User's given name.", examples=["Ada"])
    last_name: str = Field(description="User's family name.", examples=["Lovelace"])
    email: EmailStr = Field(description="Registered email address.", examples=["ada@example.com"])
    name: str = Field(description="User's display name.", examples=["Ada Lovelace"])
    email_verified: bool = Field(
        description="Whether the registered email has been verified.",
        examples=[False],
    )
