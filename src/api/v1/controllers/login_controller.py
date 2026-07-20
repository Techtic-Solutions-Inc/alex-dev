"""Login API controller."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.v1.schemas.login_schema import LoginRequest, LoginResponse
from src.config.database import get_db
from src.exceptions import InvalidCredentialsError, invalid_credentials_http_exception
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    """Authenticate a user and return a JWT access token."""
    auth_service = AuthService(db)

    try:
        user = auth_service.authenticate_user(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise invalid_credentials_http_exception() from exc

    access_token = auth_service.create_access_token(subject=user.email)
    return LoginResponse(access_token=access_token, email=user.email)
