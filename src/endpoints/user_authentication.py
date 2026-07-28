import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.user_authentication import (
    AuthenticateRequest,
    AuthenticateResponse,
    ErrorDetail,
)
from src.services.user_service import AuthenticationError, UserService, get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/authenticate",
    response_model=AuthenticateResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorDetail},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorDetail},
    },
    summary="Authenticate user with email and password",
)
def authenticate_user(
    request: AuthenticateRequest,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> AuthenticateResponse:
    try:
        session = user_service.authenticate_user(
            db=db,
            email=request.email,
            password=request.password,
        )
    except AuthenticationError as exc:
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.error_code == "service_unavailable"
            else status.HTTP_401_UNAUTHORIZED
        )
        logger.warning("Authentication failed for %s: %s", request.email, exc.message)
        raise HTTPException(
            status_code=status_code,
            detail={"error": exc.error_code, "message": exc.message},
        ) from exc

    return AuthenticateResponse(
        access_token=session.access_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
        redirect_url=session.redirect_url,
        email=session.email,
    )
