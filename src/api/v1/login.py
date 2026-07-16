from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse
from src.services.auth_service import login_user
from src.utils.logger import logger

router = APIRouter()


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
    try:
        return login_user(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
