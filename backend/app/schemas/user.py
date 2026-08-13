import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """Request body for user registration."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's last name",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address for the new account",
        examples=["john.doe@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description=(
            "Account password; must be at least 8 characters and contain "
            "at least one letter and one number"
        ),
        examples=["securePassword123"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Must be true to confirm acceptance of the Terms of Use "
            "and Privacy Policy"
        ),
        examples=[True],
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_and_validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_accepted(cls, value: bool) -> bool:
        if not value:
            raise ValueError(
                "You must accept the Terms of Use and Privacy Policy"
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        return value


def _build_full_name(first_name: str, last_name: str) -> str:
    return " ".join(part for part in (first_name, last_name) if part)


class SignupUserData(BaseModel):
    """Registered user data returned after successful signup."""

    id: str = Field(
        ...,
        description="Unique identifier for the created user",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str = Field(
        ...,
        description="User's first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        description="User's last name",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["john.doe@example.com"],
    )
    name: str = Field(
        ...,
        description="Full name derived from first and last name",
        examples=["John Doe"],
    )
    phone: str = Field(
        default="",
        description="Contact phone number",
        examples=["+1-555-0100"],
    )
    phone_number: str = Field(
        default="",
        description="Alias of phone for frontend compatibility",
        examples=["+1-555-0100"],
    )

    @classmethod
    def from_user(cls, user: object) -> "SignupUserData":
        phone = getattr(user, "phone", None) or ""
        first_name = str(getattr(user, "first_name"))
        last_name = str(getattr(user, "last_name"))
        return cls(
            id=str(getattr(user, "id")),
            first_name=first_name,
            last_name=last_name,
            email=getattr(user, "email"),
            name=_build_full_name(first_name, last_name),
            phone=phone,
            phone_number=phone,
        )


class SignupResponse(BaseModel):
    """Success response for user registration."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Account created successfully"],
    )
    data: SignupUserData


class UserCreate(BaseModel):
    """Schema for creating a new user (internal use)."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    terms_accepted: bool


class UserResponse(BaseModel):
    """Schema for user response data."""

    id: uuid.UUID = Field(..., description="Unique user identifier")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: EmailStr = Field(..., description="User email address")

    model_config = {"from_attributes": True}


class SignInRequest(BaseModel):
    """Request body for user sign-in."""

    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Account password",
        examples=["password123"],
    )
    remember_me: bool = Field(
        default=False,
        description=(
            "When true, extends the JWT session duration for persistent login"
        ),
        examples=[True],
    )

    @field_validator("email")
    @classmethod
    def validate_email_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Email is required")
        return stripped

    @field_validator("password")
    @classmethod
    def validate_password_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("Password is required")
        return value


class SignInTokenData(BaseModel):
    """JWT token and user profile returned after successful sign-in."""

    access_token: str = Field(
        ...,
        description="Signed JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        "bearer",
        description="Token type for Authorization header",
        examples=["bearer"],
    )
    expires_in: int = Field(
        ...,
        description="Token lifetime in seconds",
        examples=[1800],
    )
    id: str = Field(
        ...,
        description="Unique identifier for the authenticated user",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str = Field(
        ...,
        description="User's first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        description="User's last name",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["john.doe@example.com"],
    )
    name: str = Field(
        ...,
        description="Full name derived from first and last name",
        examples=["John Doe"],
    )
    phone: str = Field(
        default="",
        description="Contact phone number",
        examples=["+1-555-0100"],
    )
    phone_number: str = Field(
        default="",
        description="Alias of phone for frontend compatibility",
        examples=["+1-555-0100"],
    )

    @classmethod
    def from_auth_result(
        cls,
        user: object,
        *,
        access_token: str,
        token_type: str,
        expires_in: int,
    ) -> "SignInTokenData":
        phone = getattr(user, "phone", None) or ""
        first_name = str(getattr(user, "first_name"))
        last_name = str(getattr(user, "last_name"))
        return cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            id=str(getattr(user, "id")),
            first_name=first_name,
            last_name=last_name,
            email=getattr(user, "email"),
            name=_build_full_name(first_name, last_name),
            phone=phone,
            phone_number=phone,
        )


class SignInResponse(BaseModel):
    """Success response for user sign-in."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Signed in successfully"],
    )
    data: SignInTokenData
