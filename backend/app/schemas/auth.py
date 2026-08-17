"""Authentication request and response schemas."""

from pydantic import BaseModel, Field

from app.schemas.common import SuccessResponse


class RefreshTokenRequest(BaseModel):
    """Request body used to exchange a valid refresh token."""

    refresh_token: str = Field(
        min_length=20,
        description="Unexpired refresh JWT previously issued by the API.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.signature"],
    )


class TokenData(BaseModel):
    """New access token returned after a valid refresh token exchange."""

    access_token: str = Field(
        description="New signed JWT for Authorization: Bearer requests.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.signature"],
    )
    token_type: str = Field(
        default="bearer",
        description="Authentication scheme for the access token.",
        examples=["bearer"],
    )
    expires_in: int = Field(
        description="Access-token lifetime in seconds.",
        examples=[3600],
    )


RefreshTokenResponse = SuccessResponse[TokenData]
