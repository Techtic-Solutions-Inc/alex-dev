from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import get_auth0_service
from src.api.services.auth_service import (
    build_login_response_data,
    build_session_response_data,
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

_SESSION_OPENAPI_RESPONSES = {
    200: {
        "description": "Session is valid.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Session is valid.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "title": "Session active",
                        "message": "Your session is active.",
                        "description": "You are signed in to Agentwise.",
                        "link": "/dashboard",
                        "redirect": "/dashboard",
                    },
                }
            }
        },
    },
    401: {
        "description": "Missing or invalid authentication token.",
        "content": {
            "application/json": {
                "examples": {
                    "not_authenticated": {
                        "summary": "No token provided",
                        "value": {"detail": "Not authenticated"},
                    },
                    "invalid_token": {
                        "summary": "Invalid or expired token",
                        "value": {
                            "success": False,
                            "message": "Invalid or expired token.",
                            "error": {"code": "UNAUTHORIZED", "details": None},
                        },
                    },
                }
            },
        },
    },
    403: {
        "description": "Forbidden access to session information.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "You do not have permission to perform this action.",
                    "error": {"code": "FORBIDDEN", "details": None},
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


def _session_payload(current_user: User) -> dict:
    """Return the standard session success envelope."""
    return {
        "success": True,
        "message": "Session is valid.",
        "data": build_session_response_data(current_user),
    }


@router.post(
    "/api/auth/login",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in with email and password",
    description=(
        "Authenticate a user with their email address and password. "
        "When Auth0 is configured, credentials are validated against Auth0 before "
        "issuing a local JWT access token. "
        "Returns a JWT access token on success. "
        "Set `remember_me` to true to extend the session lifetime for returning users. "
        "No authentication is required."
    ),
    tags=["Authentication"],
    operationId="loginUser",
    responses={
        200: {
            "description": "Successful sign-in returns a JWT access token.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Signed in successfully.",
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "expires_in": 3600,
                            "title": "Welcome back",
                            "message": "You have signed in successfully.",
                            "description": (
                                "Everything you need to create standout real estate content."
                            ),
                            "link": "/dashboard",
                            "redirect": "/dashboard",
                        },
                    }
                }
            }
        },
        401: _SESSION_OPENAPI_RESPONSES[401],
        403: _SESSION_OPENAPI_RESPONSES[403],
        500: _SESSION_OPENAPI_RESPONSES[500],
    },
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
    auth0_service=Depends(get_auth0_service),
) -> LoginSuccessResponse:
    """Authenticate user and return JWT access token."""
    login_request = await request.json()
    user = login_user(db, login_request, auth0_service)
    return build_login_response_data(user)
