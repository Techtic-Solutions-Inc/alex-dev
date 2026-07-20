from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.services.auth_service import authenticate_user, create_access_token
from src.config.settings import settings

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse, summary="User Login", description="Authenticate user and return access token.", responses={401: {"description": "Unauthorized"}, 422: {"description": "Unprocessable Entity"}})
async def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return LoginResponse(access_token=access_token)
