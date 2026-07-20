from fastapi import APIRouter, HTTPException, status
from src.api.v1.schemas.register_schema import UserCreate, UserResponse
from src.services.user_service import create_user
from src.utils.email import send_confirmation_email

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Register a new user.
    """
    try:
        new_user = await create_user(user)
        await send_confirmation_email(new_user.email)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))