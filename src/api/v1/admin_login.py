from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse
from src.services.admin_auth_service import login_admin
from src.utils.logger import logger

router = APIRouter()


@router.post(
    "/admin/login",
    response_model=TokenResponse,
    summary="Admin login",
    description="Authenticate an admin with email and password and return a JWT session token.",
    responses={
        400: {"description": "Invalid input"},
        401: {"description": "Invalid credentials"},
    },
)
async def admin_login(
    request: LoginRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    logger.info("Admin login attempt for email=%s", request.email)
    try:
        return login_admin(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
