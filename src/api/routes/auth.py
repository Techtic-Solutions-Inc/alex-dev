```python
from fastapi import APIRouter, Depends, HTTPException, status
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
from src.schemas.auth import (
    LoginRequest,
    LoginSuccessResponse,
    SessionSuccessResponse,
)
from src.utils.token import generate_access_token

router = APIRouter()

_LOGIN_OPENAPI_RESPONSES = {
    200: {
        "description": "Login successful.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Signed in successfully.",
                    "data": {
                        "access_token": "jwt_token",
                        "expires_in": 3600,
                    },
                }
            }
        },
    },
    400: {
        "description": "Invalid input.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Invalid email or password.",
                    "error": {"code": "INVALID_INPUT", "details": "Email and password are required."},
                }
            }
        },
    },
    409: {
        "description": "Conflict error.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Incorrect password.",
                    "error": {"code": "INCORRECT_PASSWORD", "details": "The password provided is incorrect."},
                }
            }
        },
    },
    500: {
        "description": "Unexpected server error.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal Server Error",
                    "success": False,
                    "message": "Internal Server Error",
                    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                }
            }
        },
    },
}

@router.post(
    "/api/auth/login",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign in with email and password",
    description=(
        "Authenticate a user with their email address and password. "
        "When Auth0 is configured, credentials are validated against Auth0 before "
        "issuing a local JWT access token. "
        "Returns a JWT access token on success (HTTP 201). "
        "Set `remember_me` to true to extend the session lifetime for returning users. "
        "Empty email or password fields return HTTP 400. "
        "Incorrect password attempts return HTTP 409. "
        "No authentication is required."
    ),
    responses=_LOGIN_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    auth0_service: Auth0AuthenticationService = Depends(get_auth0_service_dependency),
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    return _perform_login(request, db, auth0_service)

@router.post(
    "/api/auth/signin",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign in with email and password (alias)",
    description=(
        "Alias of `POST /api/auth/login` for frontend Sign In form compatibility. "
        "Authenticate a user with their email address and password and return a JWT "
        "access token. Empty fields return HTTP 400; incorrect password returns "
        "HTTP 409. No authentication is required."
    ),
    responses=_LOGIN_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def signin(
    request: LoginRequest,
    db: Session = Depends(get_db),
    auth0_service: Auth0AuthenticationService = Depends(get_auth0_service_dependency),
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    return _perform_login(request, db, auth0_service)
```