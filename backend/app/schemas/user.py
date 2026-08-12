from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields for request validation."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Unique username for the user",
        examples=["johndoe"],
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["john@example.com"],
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""



class UserResponse(UserBase):
    """Schema for user response data."""

    model_config = {"from_attributes": True}
