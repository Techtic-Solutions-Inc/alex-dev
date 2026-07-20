"""Pydantic schemas for login requests and responses."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials submitted for authentication."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Successful login response with access token."""

    access_token: str
    token_type: str = "bearer"
    email: EmailStr
