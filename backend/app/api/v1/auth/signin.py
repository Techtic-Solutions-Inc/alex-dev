from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.common import ErrorResponse
from app.schemas.user import SignInRequest, SignInResponse, SignInTokenData
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/signin",
    response_model=SignInResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in with email and password",
    description=(
        "Authenticates a user with email and password from the Sign In form. "
        "Returns a JWT access token on success. When `remember_me` is true, "
        "the token expiry is extended for persistent sessions. "
        "No authentication is required."
    ),
    tags=["Auth"],
    responses={
        200: {
            "description": "Authentication successful; JWT token returned",
            "model": SignInResponse,
        },
        400: {
            "description": "Invalid or missing email/password fields",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "value": {
                                "success": False,
                                "message": "Validation error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "details": [
                                        {
                                            "field": "email",
                                            "message": (
                                                "value is not a valid email address"
                                            ),
                                        }
                                    ],
                                },
                            },
                        },
                        "empty_fields": {
                            "summary": "Empty email or password",
                            "value": {
                                "success": False,
                                "message": "Validation error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "details": [
                                        {
                                            "field": "email",
                                            "message": "Email is required",
                                        },
                                        {
                                            "field": "password",
                                            "message": "Password is required",
                                        },
                                    ],
                                },
                            },
                        },
                    }
                }
            },
        },
        401: {
            "description": "Incorrect email or password",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Incorrect email or password",
                        "error": {
                            "code": "INVALID_CREDENTIALS",
                            "details": None,
                        },
                    }
                }
            },
        },
        403: {
            "description": "Account is locked",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": (
                            "Your account has been locked. "
                            "Please contact support."
                        ),
                        "error": {
                            "code": "ACCOUNT_LOCKED",
                            "details": None,
                        },
                    }
                }
            },
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
async def signin(
    body: SignInRequest,
    db: Session = Depends(get_db),
) -> SignInResponse:
    """Authenticate a user and return a JWT access token."""
    auth_service = AuthService(db)
    token_data = auth_service.authenticate_user(body)

    return SignInResponse(
        success=True,
        message="Signed in successfully",
        data=SignInTokenData(
            access_token=str(token_data["access_token"]),
            token_type=str(token_data["token_type"]),
            expires_in=int(token_data["expires_in"]),
        ),
    )
