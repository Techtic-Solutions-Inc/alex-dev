from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.services.user_service import (
    confirm_user_email,
    create_user_with_confirmation,
    validate_signup_required_fields,
)
from src.config.database import get_db
from src.config.settings import get_settings
from src.schemas.auth import (
    ConfirmEmailSuccessResponse,
    SignupRequest,
    SignupSuccessResponse,
)

settings = get_settings()
router = APIRouter()

@router.post(
    '/signup',
    response_model=SignupSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_SIGNUP_OPENAPI_RESPONSES,
    summary='Register a new user',
    description='Register a new user by providing necessary details such as first name, last name, email, and password. A confirmation email will be sent to the provided email address.',
    tags=['User Management']
)
async def signup(
    signup_request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user and send a confirmation email.
    """
    validate_signup_required_fields(signup_request)
    user, confirmation_link = create_user_with_confirmation(signup_request, db)
    return _build_signup_response(user, confirmation_link)
