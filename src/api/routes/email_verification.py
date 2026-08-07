from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.api.services.user_service import request_email_verification
from src.config.database import get_db
from src.schemas.email_verification import EmailVerificationRequest, EmailVerificationSuccessResponse

router = APIRouter()

@router.post('/email-verification', response_model=EmailVerificationSuccessResponse, status_code=status.HTTP_201_CREATED, summary='Request email verification', description='Allows users to request an email verification link to be sent to their registered email address.')
async def request_email_verification(body: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Request an email verification link to be sent to the user's email."""
    return request_email_verification(body, db)
