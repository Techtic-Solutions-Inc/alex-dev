from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService
from src.api.services.auth_service import (
    build_login_response_data,
    build_session_response_data,
    get_auth0_service_dependency,
    login_user,
)
from src.config.database import get_db
from src.exceptions import UnauthorizedError
from src.middlewares.auth import get_current_user_record
from src.schemas.auth import (
    LoginRequest,
    LoginSuccessResponse,
    SessionSuccessResponse,
)
from src.utils.token import generate_access_token

router = APIRouter()

@router.post(
    '/auth/login',
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_LOGIN_OPENAPI_RESPONSES,
    summary='User login',
    description='Authenticate a user by validating their email and password. Returns a JWT access token upon successful authentication.',
    tags=['Authentication']
)
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    """
    user = login_user(login_request, db)
    return build_login_response_data(user)
