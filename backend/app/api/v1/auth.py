"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.common.guards.jwt import get_current_subject
from app.core.security import create_access_token
from app.exceptions.http_exceptions import AppHTTPException
from app.schemas.common import SuccessResponse

router = APIRouter(tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="The username of the user")
    password: str = Field(..., min_length=1, description="The password of the user")


class LoginData(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of the token")


class SubjectData(BaseModel):
    subject: str = Field(..., description="Authenticated user identifier")


LoginResponse = SuccessResponse[LoginData]
MeResponse = SuccessResponse[SubjectData]


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Authenticate user",
    description="Authenticates a user and returns a JWT token.",
)
async def login(body: LoginRequest) -> LoginResponse:
    if body.username != "johndoe" or body.password != "secret":
        raise AppHTTPException(401, "INVALID_CREDENTIALS", "Invalid credentials.")
    token = create_access_token(body.username)
    return SuccessResponse(
        message="Login successful.",
        data=LoginData(access_token=token, token_type="bearer"),
    )


@router.get(
    "/auth/me",
    response_model=MeResponse,
    summary="Get authenticated subject",
    description="Returns the subject encoded in a valid access token.",
)
async def me(
    subject: Annotated[str, Depends(get_current_subject)],
) -> MeResponse:
    return SuccessResponse(
        message="Authenticated.",
        data=SubjectData(subject=subject),
    )
