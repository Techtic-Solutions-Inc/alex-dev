from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.auth import LoginRequest, LoginResponse, SessionResponse
from src.api.services.auth_service import login_user, get_user_session
from src.config.settings import settings
from loguru import logger

router = APIRouter()

@router.post("/api/auth/login", response_model=LoginResponse, summary="User login", description="Authenticate user and return session token.")
async def login(request: LoginRequest):
    """Authenticate user and return session token."""
    try:
        token = await login_user(request.email, request.password)
        return LoginResponse(success=True, message="Login successful", data={"token": token})
    except ValueError as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/api/auth/session", response_model=SessionResponse, summary="Get user session", description="Retrieve current user session details.")
async def get_session(token: str = Depends(get_user_session)):
    """Retrieve current user session details."""
    return SessionResponse(success=True, message="Session retrieved", data=token)
