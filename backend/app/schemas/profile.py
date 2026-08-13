import re

from pydantic import BaseModel, EmailStr, Field, field_validator


_MOBILE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,20}$")
_PASSWORD_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_DIGIT = re.compile(r"\d")


class ProfileAddressData(BaseModel):
    """Address object returned in profile responses (empty strings allowed)."""

    street: str = Field(
        default="",
        max_length=255,
        description="Street address line",
        examples=["123 Main St"],
    )
    city: str = Field(
        default="",
        max_length=100,
        description="City name",
        examples=["Anytown"],
    )
    state: str = Field(
        default="",
        max_length=100,
        description="State or province",
        examples=["CA"],
    )
    zip: str = Field(
        default="",
        max_length=20,
        description="ZIP or postal code",
        examples=["12345"],
    )
    country: str = Field(
        default="",
        max_length=100,
        description="Country name",
        examples=["USA"],
    )


class AddressSchema(BaseModel):
    """Postal address nested under the user profile."""

    street: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Street address line",
        examples=["123 Main St"],
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name",
        examples=["Anytown"],
    )
    state: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="State or province",
        examples=["CA"],
    )
    zip: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="ZIP or postal code",
        examples=["12345"],
    )
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Country name",
        examples=["USA"],
    )

    @field_validator("street", "city", "state", "zip", "country")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped


class ProfileUpdateRequest(BaseModel):
    """Request body for updating the authenticated user's profile."""

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
        description="User's email address",
        examples=["john.doe@example.com"],
    )
    mobile_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mobile phone number",
        examples=["1234567890"],
    )
    bio: str = Field(
        ...,
        max_length=2000,
        description="Short biography shown on the Profile screen",
        examples=["This is my bio."],
    )
    address: AddressSchema = Field(
        ...,
        description="Postal address including street, city, state, ZIP, and country",
    )
    time_zone: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Preferred time zone identifier",
        examples=["GMT-4"],
    )

    @field_validator("first_name", "last_name", "time_zone")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped

    @field_validator("bio")
    @classmethod
    def strip_bio(cls, value: str) -> str:
        return value.strip()

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        if not _MOBILE_PATTERN.match(stripped):
            raise ValueError("Invalid mobile number format")
        return stripped

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("This field is required")
        return stripped


class ProfileData(BaseModel):
    """Profile fields returned by GET/PUT profile endpoints."""

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
        description="User's email address",
        examples=["john.doe@example.com"],
    )
    mobile_number: str = Field(
        ...,
        description="Mobile phone number",
        examples=["1234567890"],
    )
    bio: str = Field(
        ...,
        description="Short biography",
        examples=["This is my bio."],
    )
    address: ProfileAddressData = Field(
        ...,
        description="Postal address",
    )
    time_zone: str = Field(
        ...,
        description="Preferred time zone",
        examples=["GMT-4"],
    )

    @classmethod
    def from_user(cls, user: object) -> "ProfileData":
        return cls(
            first_name=str(getattr(user, "first_name") or ""),
            last_name=str(getattr(user, "last_name") or ""),
            email=getattr(user, "email"),
            mobile_number=str(getattr(user, "mobile_number") or ""),
            bio=str(getattr(user, "bio") or ""),
            address=ProfileAddressData(
                street=str(getattr(user, "address_street") or ""),
                city=str(getattr(user, "address_city") or ""),
                state=str(getattr(user, "address_state") or ""),
                zip=str(getattr(user, "address_zip") or ""),
                country=str(getattr(user, "address_country") or ""),
            ),
            time_zone=str(getattr(user, "time_zone") or ""),
        )


class ProfileResponse(BaseModel):
    """Success envelope for profile GET/PUT."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Profile retrieved successfully"],
    )
    data: ProfileData


class ChangePasswordRequest(BaseModel):
    """Request body for changing the authenticated user's password."""

    current_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The user's current password",
        examples=["securePassword123"],
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description=(
            "New account password; must be at least 8 characters and contain "
            "at least one letter and one number"
        ),
        examples=["newSecurePassword456"],
    )

    @field_validator("current_password")
    @classmethod
    def current_password_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Current password is required")
        return value

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, value: str) -> str:
        if not _PASSWORD_LETTER.search(value):
            raise ValueError("Password must contain at least one letter")
        if not _PASSWORD_DIGIT.search(value):
            raise ValueError("Password must contain at least one number")
        return value


class ChangePasswordData(BaseModel):
    """Payload returned after a successful password change."""

    id: str = Field(
        ...,
        description="Unique identifier for the user whose password was changed",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )


class ChangePasswordResponse(BaseModel):
    """Success envelope for change-password."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Password changed successfully"],
    )
    data: ChangePasswordData
