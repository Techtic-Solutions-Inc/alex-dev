from fastapi import APIRouter, Depends
from src.api.v1.services.auth_service import AuthService
from src.api.v1.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()

def get_auth_service():
    return AuthService()

@router.post('/login', response_model=TokenResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(request)
