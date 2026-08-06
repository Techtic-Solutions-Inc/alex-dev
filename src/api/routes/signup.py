from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.services.user_service import confirm_user_email, create_user_with_confirmation
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
    "/signup",
    response_model=SignupSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Create a new user account with an email address and password. "
        "The email must be unique and the password must meet strength requirements. "
        "Upon successful registration, a confirmation email is sent via SendGrid. "
        "No authentication is required."
    ),
    responses={
        201: {
            "description": "User registered successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": (
                            "Account created successfully. "
                            "Please confirm your email."
                        ),
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "title": "Account created",
                            "message": "Please check your email to confirm your account.",
                            "description": (
                                "We sent a confirmation email to your inbox. "
                                "Click the link in that email to activate your account."
                            ),
                            "link": None,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid email format or weak password.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "value": {
                                "success": False,
                                "message": "Invalid email format.",
                                "error": {"code": "INVALID_EMAIL", "details": None},
                            },
                        },
                        "weak_password": {
                            "summary": "Password does not meet requirements",
                            "value": {
                                "success": False,
                                "message": (
                                    "Password must be at least 8 characters long and "
                                    "include an uppercase letter, a number, and a "
                                    "special character."
                                ),
                                "error": {
                                    "code": "WEAK_PASSWORD",
                                    "details": {"field": "password"},
                                },
                            },
                        },
                    }
                }
            },
        },
        409: {
            "description": "Email address is already registered.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "An account with this email address already exists.",
                        "error": {
                            "code": "EMAIL_ALREADY_EXISTS",
                            "details": {"field": "email"},
                        },
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
    },
)
async def signup_user(
    request: SignupRequest, db: Session = Depends(get_db)
) -> SignupSuccessResponse:
    """Register a new user and send confirmation email."""
    return await create_user_with_confirmation(request, db)
