from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.auth import LoginRequest, LoginResponse, SessionResponse
from src.api.services.auth_service import login_user, get_user_session
from src.api.dependencies import get_db
from src.api.exceptions import AuthException

router = APIRouter()

@router.post('/api/auth/login', response_model=LoginResponse, summary="User login", description="Authenticate user and return session token.")
async def login(request: LoginRequest, db=Depends(get_db)):
    try:
        user_session = await login_user(request.email, request.password, db)
        return LoginResponse(success=True, message="Login successful", data=user_session)
    except AuthException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get('/api/auth/session', response_model=SessionResponse, summary="Get user session", description="Retrieve current user session details.")
async def get_session(db=Depends(get_db)):
    try:
        session_data = await get_user_session(db)
        return SessionResponse(success=True, message="Session retrieved", data=session_data)
    except AuthException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))