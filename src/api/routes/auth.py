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

@router.post('/api/auth/login', response_model=LoginSuccessResponse, summary='User login', description='Authenticate a user and return a JWT access token. This endpoint requires valid email and password credentials. Upon successful authentication, a JWT token is returned which can be used for subsequent requests requiring authentication.')
async def login(body: LoginRequest, db: Session = Depends(get_db), auth_service: Auth0AuthenticationService = Depends(get_auth0_service_dependency)):
    # Implementation here
    pass

_LOGIN_OPENAPI_RESPONSES = {
    201: {
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
        },
    },
    400: {
        "description": "Empty or invalid login fields.",
        "content": {
            "application/json": {
                "examples": {
                    "empty_email": {
                        "summary": "Empty email",
                        "value": {
                            "success": False,
                            "message": "Email is required.",
                            "error": {
                                "code": "EMPTY_EMAIL",
                                "details": {"field": "email"},
                            },
                        },
                    },
                    "empty_password": {
                        "summary": "Empty password",
                        "value": {
                            "success": False,
                            "message": "Password is required.",
                            "error": {
                                "code": "EMPTY_PASSWORD",
                                "details": {"field": "password"},
                            },
                        },
                    },
                    "invalid_email": {
                        "summary": "Invalid email format",
                        "value": {
                            "success": False,
                            "message": "Invalid email format.",
                            "error": {
                                "code": "INVALID_EMAIL",
                                "details": {"field": "email"},
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Authentication service unavailable or unauthorized.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication service is temporarily unavailable.",
                    "error": {
                        "code": "AUTHENTICATION_SERVICE_ERROR",
                        "details": None,
                    },
                }
            }
        },
    },
    403: {
        "description": "Forbidden.",
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
    409: {
        "description": "Incorrect email or password.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Incorrect email or password.",
                    "error": {"code": "INCORRECT_PASSWORD", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Request body validation error.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation Error",
                    "error": {"code": "VALIDATION_ERROR", "details": None},
                }
            }
        },
    },
}
