from pydantic import BaseModel, EmailStr, Field


class AuthenticateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthenticateResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    redirect_url: str
