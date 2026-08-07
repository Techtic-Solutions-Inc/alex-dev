from fastapi import APIRouter, HTTPException, status
from src.api.schemas.signup import SignupRequest, SignupResponse
from src.api.services.user_service import create_user_with_confirmation
from loguru import logger

router = APIRouter()

@router.post("/api/auth/signup", response_model=SignupResponse, summary="User signup", description="Register a new user and send confirmation email.")
async def signup(request: SignupRequest):
    """Register a new user and send confirmation email."""
    try:
        user_id = await create_user_with_confirmation(request)
        return SignupResponse(success=True, message="Signup successful", data={"user_id": user_id})
    except ValueError as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
