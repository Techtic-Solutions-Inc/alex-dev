"""Authentication request and response schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials for user login."""

    username: str = Field(..., min_length=1, description="Account username.")
    password: str = Field(..., min_length=1, description="Account password.")


class LoginResponse(BaseModel):
    """Successful login response."""

    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")
    expires_in: int = Field(..., description="Token lifetime in seconds.")
