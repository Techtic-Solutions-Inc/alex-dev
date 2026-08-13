from pydantic import BaseModel, Field

from app.models.user import User
from app.schemas.common import SuccessResponse


class UserDetailsData(BaseModel):
    """Logged-in user details for the Content Library screen."""

    user_id: str = Field(
        ...,
        description="Authenticated user's UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="Display name (first name and last name)",
        examples=["John Doe"],
    )
    ai_credit_usage: int = Field(
        ...,
        ge=0,
        description="Current AI credit usage count for the authenticated user",
        examples=[42],
    )

    @classmethod
    def from_user(cls, user: User) -> "UserDetailsData":
        """Build response data from a User ORM instance."""
        name = f"{user.first_name} {user.last_name}".strip()
        return cls(
            user_id=str(user.id),
            name=name,
            ai_credit_usage=int(user.ai_credit_usage or 0),
        )


class UserDetailsResponse(SuccessResponse[UserDetailsData]):
    """Success envelope for Content Library user details."""

    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["User details retrieved successfully"],
    )
    data: UserDetailsData
