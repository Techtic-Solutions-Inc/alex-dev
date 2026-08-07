from fastapi import APIRouter, Depends, HTTPException, status
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
from loguru import logger

router = APIRouter()

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
                    "detail": "Validation Error",
                    "errors": [
                        {"field": "email", "message": "Field required"},
                        {"field": "password", "message": "Field required"},
                    ],
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
        "description": "Invalid or expired authentication token.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Invalid or expired token.",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            },
        },
    },
    403: {
        "description": "Missing JWT token or forbidden access to session information.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication is required to access this resource.",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "Authenticated user was not found.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "User not found.",
                    "error": {"code": "USER_NOT_FOUND", "details": None},
                }
            }
        },
    },
}

@router.post("/login", response_model=LoginSuccessResponse, responses=_LOGIN_OPENAPI_RESPONSES)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return build_login_response_data(user)

@router.get("/session", response_model=SessionSuccessResponse, responses=_SESSION_OPENAPI_RESPONSES)
def get_session(user: User = Depends(get_current_user_record)):
    return build_session_response_data(user)
