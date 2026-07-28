from pydantic import BaseModel, EmailStr, Field


class AuthenticateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthenticatedUserResponse(BaseModel):
    id: str
    email: str


class AuthenticateResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    redirect_url: str
    user: AuthenticatedUserResponse


class ErrorResponse(BaseModel):
    detail: str
