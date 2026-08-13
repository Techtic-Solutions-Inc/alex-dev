from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.common import ErrorResponse
from app.schemas.password_recovery import (
    PasswordRecoveryRequest,
    PasswordRecoveryResponse,
)
from app.services.password_recovery_service import PasswordRecoveryService

router = APIRouter()


@router.post(
    "/password-recovery",
    response_model=PasswordRecoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate password recovery",
    description=(
        "Starts the Forgot Password flow for the given email address. "
        "Validates that the email is present and well-formed, confirms an "
        "account exists (users accepted Terms of Use and Privacy Policy at "
        "signup), then emails a password reset link that expires after "
        "30 minutes. No authentication is required."
    ),
    tags=["Auth"],
    responses={
        200: {
            "description": "Password recovery email sent successfully",
            "model": PasswordRecoveryResponse,
        },
        400: {
            "description": "Invalid or missing email, or email delivery failure",
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
                        "empty_email": {
                            "summary": "Empty email field",
                            "value": {
                                "success": False,
                                "message": "Validation error",
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "details": [
                                        {
                                            "field": "email",
                                            "message": "Email is required",
                                        }
                                    ],
                                },
                            },
                        },
                        "email_send_failed": {
                            "summary": "Email provider failure",
                            "value": {
                                "success": False,
                                "message": (
                                    "Unable to send password recovery email. "
                                    "Please try again later."
                                ),
                                "error": {
                                    "code": "EMAIL_SEND_FAILED",
                                    "details": None,
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
            "description": "No account exists for the provided email",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": (
                            "No account is associated with this email address"
                        ),
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "details": None,
                        },
                    }
                }
            },
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
async def password_recovery(
    body: PasswordRecoveryRequest,
    db: Session = Depends(get_db),
) -> PasswordRecoveryResponse:
    """Send a time-limited password reset email to a registered user."""
    service = PasswordRecoveryService(db)
    data = service.initiate_password_recovery(body)

    return PasswordRecoveryResponse(
        success=True,
        message="Password recovery email sent successfully",
        data=data,
    )
