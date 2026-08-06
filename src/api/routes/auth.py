"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth_service import login_user
from src.config.database import get_db
from src.middlewares.auth import get_current_user_record
from src.schemas.auth import (
    LoginRequest,
    LoginSuccessResponse,
    ValidateSessionSuccessResponse,
)
from src.utils.token import generate_access_token

router = APIRouter()


@router.post(
    "/api/auth/login",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in with email and password",
    description=(
        "Authenticate a user with their email address and password. "
        "Returns a JWT access token on success. "
        "Set `remember_me` to true to extend the session lifetime for returning users. "
        "No authentication is required."
    ),
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
                        },
                    }
                }
            },
        },
        401: {
            "description": "Invalid email or password.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid email or password.",
                        "error": {"code": "INVALID_CREDENTIALS", "details": None},
                    }
                }
            },
        },
        422: {
            "description": "Request body validation error.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_fields": {
                            "summary": "Required fields missing",
                            "value": {
                                "success": False,
                                "message": "Validation Error",
                                "error": {"code": "VALIDATION_ERROR", "details": None},
                                "detail": "Validation Error",
                                "errors": [
                                    {"field": "email", "message": "Field required"},
                                    {"field": "password", "message": "Field required"},
                                ],
                            },
                        },
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "value": {
                                "success": False,
                                "message": "Validation Error",
                                "error": {"code": "VALIDATION_ERROR", "details": None},
                                "detail": "Validation Error",
                                "errors": [
                                    {
                                        "field": "email",
                                        "message": "Invalid email format.",
                                    }
                                ],
                            },
                        },
                        "short_password": {
                            "summary": "Password too short",
                            "value": {
                                "success": False,
                                "message": "Validation Error",
                                "error": {"code": "VALIDATION_ERROR", "details": None},
                                "detail": "Validation Error",
                                "errors": [
                                    {
                                        "field": "password",
                                        "message": (
                                            "String should have at least 8 characters"
                                        ),
                                    }
                                ],
                            },
                        },
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
    },
    tags=["Authentication"],
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    user, expires_in = login_user(
        db,
        email=request.email,
        password=request.password,
        remember_me=request.remember_me,
    )

    token = generate_access_token(
        {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        },
        expires_in_seconds=expires_in,
    )

    return {
        "success": True,
        "message": "Signed in successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "title": "Welcome back",
            "message": "You have signed in successfully.",
            "description": (
                "Everything you need to create standout real estate content."
            ),
            "link": "/dashboard",
        },
    }


@router.get(
    "/api/auth/validate",
    response_model=ValidateSessionSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate the current user session",
    description=(
        "Validate the JWT access token supplied in the Authorization header and "
        "return the authenticated user's session details. "
        "Requires a valid Bearer token."
    ),
    responses={
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
                }
            },
        },
        403: {
            "description": "Forbidden access to session validation.",
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
    },
    tags=["Authentication"],
)
def validate_session(
    current_user: User = Depends(get_current_user_record),
) -> dict:
    """Validate the current JWT session and return user details."""
    return {
        "success": True,
        "message": "Session is valid.",
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "title": "Session active",
            "message": "Your session is active.",
            "description": "You are signed in to Agentwise.",
            "link": "/dashboard",
        },
    }
