from pydantic import BaseModel, EmailStr, Field


class AuthenticateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthenticateResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    redirect_url: str
    email: str


class ErrorDetail(BaseModel):
    error: str
    message: str
