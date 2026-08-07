from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.api.services.auth_service import request_password_reset
from src.config.database import get_db
from src.schemas.password_recovery import PasswordRecoveryRequest, PasswordRecoverySuccessResponse

router = APIRouter()

@router.post('/password-recovery', response_model=PasswordRecoverySuccessResponse, status_code=status.HTTP_201_CREATED, summary='Request password recovery', description='Allows users to request a password reset link to be sent to their registered email address.')
async def request_password_recovery(body: PasswordRecoveryRequest, db: Session = Depends(get_db)):
    """Request a password reset link to be sent to the user's email."""
    return request_password_reset(body, db)
