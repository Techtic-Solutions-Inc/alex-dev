import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.dependencies.db import get_db
from app.exceptions.http_exceptions import ForbiddenException
from app.middleware.auth import oauth2_scheme
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.user import SignInRequest, SignInResponse, SignInTokenData
from app.services.auth_service import AuthService

router = APIRouter()


def _ensure_email_belongs_to_requesting_user(
    db: Session,
    token: str | None,
    normalized_email: str,
) -> None:
    """Prevent IDOR when an authenticated caller submits another user's email."""
    if not token:
        return

    try:
        payload = verify_token(token)
    except ValueError:
        return

    user_id = payload.get("sub")
    if not user_id:
        return

    try:
        parsed_user_id = uuid.UUID(str(user_id))
    except ValueError:
        return

    authenticated_user = db.scalar(
        select(User).where(User.id == parsed_user_id)
    )
    if authenticated_user is None:
        return

    if authenticated_user.email.strip().lower() != normalized_email:
        raise ForbiddenException(
            message="Email does not belong to the authenticated user",
            code="EMAIL_USER_MISMATCH",
        )


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
            "description": "Account is locked or email does not match authenticated user",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "account_locked": {
                            "summary": "Account is locked",
                            "value": {
                                "success": False,
                                "message": (
                                    "Your account has been locked. "
                                    "Please contact support."
                                ),
                                "error": {
                                    "code": "ACCOUNT_LOCKED",
                                    "details": None,
                                },
                            },
                        },
                        "email_user_mismatch": {
                            "summary": "Email does not belong to authenticated user",
                            "value": {
                                "success": False,
                                "message": (
                                    "Email does not belong to the authenticated user"
                                ),
                                "error": {
                                    "code": "EMAIL_USER_MISMATCH",
                                    "details": None,
                                },
                            },
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
    token: str | None = Depends(oauth2_scheme),
) -> SignInResponse:
    """Authenticate a user and return a JWT access token."""
    normalized_email = body.email.strip().lower()
    _ensure_email_belongs_to_requesting_user(db, token, normalized_email)

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
