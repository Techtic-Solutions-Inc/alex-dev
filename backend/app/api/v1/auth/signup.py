from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.common import ErrorResponse
from app.schemas.user import SignupRequest, SignupResponse, SignupUserData
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user account using the Sign Up form fields. "
        "Validates first name, last name, email, password strength, and "
        "terms acceptance. The email must be unique. Passwords are hashed "
        "before storage and are never returned in the response. "
        "No authentication is required."
    ),
    tags=["Auth"],
    responses={
        201: {
            "description": "User account created successfully",
            "model": SignupResponse,
        },
        400: {
            "description": (
                "Invalid input, duplicate email, or terms not accepted"
            ),
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_email": {
                            "summary": "Email already registered",
                            "value": {
                                "success": False,
                                "message": (
                                    "An account with this email already exists"
                                ),
                                "error": {
                                    "code": "EMAIL_ALREADY_EXISTS",
                                    "details": None,
                                },
                            },
                        },
                        "validation_error": {
                            "summary": "Missing or invalid fields",
                            "value": {
                                "success": False,
                                "message": "Validation error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "details": [
                                        {
                                            "field": "first_name",
                                            "message": "Field required",
                                        }
                                    ],
                                },
                            },
                        },
                        "terms_not_accepted": {
                            "summary": "Terms checkbox not checked",
                            "value": {
                                "success": False,
                                "message": "Validation error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "details": [
                                        {
                                            "field": "terms_accepted",
                                            "message": (
                                                "You must accept the Terms of "
                                                "Use and Privacy Policy"
                                            ),
                                        }
                                    ],
                                },
                            },
                        },
                    }
                }
            },
        },
        401: {
            "description": "Authentication required (not applicable)",
            "model": ErrorResponse,
        },
        403: {
            "description": "Access denied (not applicable)",
            "model": ErrorResponse,
        },
        404: {
            "description": "Resource not found (not applicable)",
            "model": ErrorResponse,
        },
        409: {
            "description": "Resource conflict (not applicable)",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error (not applicable)",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "An unexpected error occurred",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "details": None,
                        },
                    }
                }
            },
        },
    },
)
async def signup(
    body: SignupRequest,
    db: Session = Depends(get_db),
) -> SignupResponse:
    """Register a new user with first name, last name, email, and password."""
    auth_service = AuthService(db)
    user = auth_service.register_user(body)

    return SignupResponse(
        success=True,
        message="Account created successfully",
        data=SignupUserData.from_user(user),
    )
