from pydantic import BaseModel, EmailStr, Field


class AuthenticateRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class AuthenticateResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    redirect_url: str
