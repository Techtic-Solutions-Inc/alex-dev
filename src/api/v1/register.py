from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.auth import RegisterRequest, RegisterResponse
from src.services.email_service import EmailDeliveryError
from src.services.registration_service import DuplicateEmailError, register_user
from src.utils.logger import logger

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="User registration",
    description=(
        "Register a new user account with a unique email and strong password. "
        "Sends a confirmation email upon successful registration."
    ),
    responses={
        400: {"description": "Email already in use"},
        422: {"description": "Invalid input"},
        503: {"description": "Failed to send confirmation email"},
    },
)
async def register(
    request: RegisterRequest, db: Session = Depends(get_db)
) -> RegisterResponse:
    logger.info("Registration attempt for email=%s", request.email)
    try:
        return register_user(db, request)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
