from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.auth_service import authenticate_user, create_access_token
from src.utils.logger import logger

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate a user with email and password and return a JWT session token.",
    responses={
        400: {"description": "Invalid input"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    logger.info("Login attempt for email=%s", request.email)
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(str(user.id), {"email": user.email})
    return TokenResponse(access_token=access_token)
