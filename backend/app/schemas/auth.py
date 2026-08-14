from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """Request body for exchanging a refresh token for a new access token."""

    refresh_token: str = Field(
        ...,
        description="Valid JWT refresh token issued by the authentication service",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        min_length=1,
    )


class TokenData(BaseModel):
    """Access and refresh token pair returned by auth endpoints."""

    access_token: str = Field(
        ...,
        description="JWT access token used for authenticated API requests",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token used to obtain a new access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        "bearer",
        description="OAuth2 token type",
        examples=["bearer"],
    )


class RefreshTokenResponse(BaseModel):
    """Success response for token refresh."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["Token refreshed successfully"],
    )
    data: TokenData
