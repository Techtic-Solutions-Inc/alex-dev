"""Password recovery routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.services.auth_service import (
    request_password_reset,
    reset_password_with_token,
    validate_password_recovery_request_fields,
    validate_password_reset_token,
)
from src.config.database import get_db
from src.config.settings import get_settings
from src.exceptions import BadRequestError
from src.schemas.password_recovery import (
    PasswordRecoveryRequest,
    PasswordRecoverySuccessResponse,
    PasswordResetRequest,
    PasswordResetSuccessResponse,
    ValidateResetTokenSuccessResponse,
)

settings = get_settings()
router = APIRouter()


def _build_recovery_response(user, reset_link: str) -> dict:
    """Build the password recovery request success payload."""
    link = reset_link if settings.environment != "production" else None

    return {
        "success": True,
        "message": "Password reset link sent successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "title": "Check your email",
            "message": "We sent a password reset link to your email.",
            "description": (
                "The link is valid for 30 minutes. If you did not request a password "
                "reset, you can safely ignore this email."
            ),
            "link": link,
        },
    }


_RECOVERY_REQUEST_OPENAPI_RESPONSES = {
    201: {
        "description": "Password reset link sent successfully.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Password reset link sent successfully.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "title": "Check your email",
                        "message": "We sent a password reset link to your email.",
                        "description": (
                            "The link is valid for 30 minutes. If you did not request "
                            "a password reset, you can safely ignore this email."
                        ),
                        "link": None,
                    },
                }
            }
        },
    },
    400: {
        "description": (
            "Invalid input such as empty email, invalid email format, or terms not "
            "accepted."
        ),
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
                    "terms_not_accepted": {
                        "summary": "Terms not accepted",
                        "value": {
                            "success": False,
                            "message": (
                                "You must accept the Terms of Use and Privacy Policy."
                            ),
                            "error": {
                                "code": "TERMS_NOT_ACCEPTED",
                                "details": {"field": "terms_accepted"},
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Not applicable — password recovery is a public endpoint.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication is required to access this resource.",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            }
        },
    },
    403: {
        "description": "Not applicable — password recovery is a public endpoint.",
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
    404: {
        "description": "No account registered with the provided email address.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "No account is registered with this email address.",
                    "error": {
                        "code": "EMAIL_NOT_FOUND",
                        "details": {"field": "email"},
                    },
                }
            }
        },
    },
    409: {
        "description": "Not applicable for password recovery request.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "The request conflicts with the current state.",
                    "error": {"code": "CONFLICT", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Request body validation error (malformed payload).",
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
}


@router.post(
    "/api/password-recovery",
    response_model=PasswordRecoverySuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a password reset link",
    description=(
        "Request a password reset link for the provided email address. "
        "The email must be registered in the system and the Terms of Service and "
        "Privacy Policy must be accepted. A reset link is sent via SendGrid and "
        "expires after 30 minutes. No authentication is required.\n\n"
        "**Request fields:** `email`, `terms_accepted`.\n\n"
        "**Success (201):** returns the user id, email, and UI guidance "
        "(`title`, `message`, `description`, `link`).\n\n"
        "**Errors:** empty/invalid email or terms not accepted → 400; "
        "unregistered email → 404 (`EMAIL_NOT_FOUND`)."
    ),
    responses=_RECOVERY_REQUEST_OPENAPI_RESPONSES,
    tags=["Password Recovery"],
)
async def request_password_recovery(
    body: PasswordRecoveryRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Request a password reset link for the user.

    ``body: PasswordRecoveryRequest`` is required so OpenAPI/Swagger exposes every
    ticket field (email, terms_accepted) in Try it out.
    """
    validate_password_recovery_request_fields(body.model_dump())

    user, reset_link = request_password_reset(db, email=body.email)
    return _build_recovery_response(user, reset_link)


_VALIDATE_TOKEN_OPENAPI_RESPONSES = {
    200: {
        "description": "Password reset token is valid.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Password reset token is valid.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "title": "Reset your password",
                        "message": "Your reset link is valid.",
                        "description": (
                            "Enter a new password below to complete the reset."
                        ),
                        "link": "/reset-password",
                    },
                }
            }
        },
    },
    400: {
        "description": "Invalid or expired password reset token.",
        "content": {
            "application/json": {
                "examples": {
                    "expired_token": {
                        "summary": "Expired token",
                        "value": {
                            "success": False,
                            "message": (
                                "The password reset link has expired. "
                                "Please request a new password reset."
                            ),
                            "error": {
                                "code": "RESET_TOKEN_EXPIRED",
                                "details": None,
                            },
                        },
                    },
                    "invalid_token": {
                        "summary": "Missing token",
                        "value": {
                            "success": False,
                            "message": "A password reset token is required.",
                            "error": {"code": "INVALID_TOKEN", "details": None},
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Not applicable — token validation is a public endpoint.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication is required to access this resource.",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            }
        },
    },
    403: {
        "description": "Not applicable — token validation is a public endpoint.",
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
    404: {
        "description": "Password reset token not found or already used.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": (
                        "The password reset link is invalid or has already been used."
                    ),
                    "error": {"code": "INVALID_RESET_TOKEN", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Invalid path parameter.",
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


@router.get(
    "/api/password-recovery/validate/{token}",
    response_model=ValidateResetTokenSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate a password reset token",
    description=(
        "Validate a password reset token from the reset email link. "
        "Returns user details when the token is valid and has not expired "
        "(30-minute window). No authentication is required.\n\n"
        "**Path parameter:** `token` — the reset token from the email link.\n\n"
        "**Success (200):** returns user id, email, and UI guidance.\n\n"
        "**Errors:** expired token → 400 (`RESET_TOKEN_EXPIRED`); "
        "invalid/used token → 404 (`INVALID_RESET_TOKEN`)."
    ),
    responses=_VALIDATE_TOKEN_OPENAPI_RESPONSES,
    tags=["Password Recovery"],
)
def validate_reset_token(
    token: str,
    db: Session = Depends(get_db),
) -> dict:
    """Validate a password reset token."""
    user = validate_password_reset_token(db, token=token)

    return {
        "success": True,
        "message": "Password reset token is valid.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "title": "Reset your password",
            "message": "Your reset link is valid.",
            "description": "Enter a new password below to complete the reset.",
            "link": "/reset-password",
        },
    }


_RESET_PASSWORD_OPENAPI_RESPONSES = {
    200: {
        "description": "Password reset successfully.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Password reset successfully.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "title": "Password updated",
                        "message": "Your password has been reset successfully.",
                        "description": "You can now sign in with your new password.",
                        "link": "/sign-in",
                    },
                }
            }
        },
    },
    400: {
        "description": (
            "Invalid input such as weak password, expired token, or terms not "
            "accepted."
        ),
        "content": {
            "application/json": {
                "examples": {
                    "weak_password": {
                        "summary": "Weak password",
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
                    "expired_token": {
                        "summary": "Expired token",
                        "value": {
                            "success": False,
                            "message": (
                                "The password reset link has expired. "
                                "Please request a new password reset."
                            ),
                            "error": {
                                "code": "RESET_TOKEN_EXPIRED",
                                "details": None,
                            },
                        },
                    },
                    "terms_not_accepted": {
                        "summary": "Terms not accepted",
                        "value": {
                            "success": False,
                            "message": (
                                "You must accept the Terms of Use and Privacy Policy."
                            ),
                            "error": {
                                "code": "TERMS_NOT_ACCEPTED",
                                "details": {"field": "terms_accepted"},
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Not applicable — password reset is a public endpoint.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication is required to access this resource.",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            }
        },
    },
    403: {
        "description": "Not applicable — password reset is a public endpoint.",
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
    404: {
        "description": "Password reset token not found or already used.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": (
                        "The password reset link is invalid or has already been used."
                    ),
                    "error": {"code": "INVALID_RESET_TOKEN", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Not applicable for password reset.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "The request conflicts with the current state.",
                    "error": {"code": "CONFLICT", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Request body validation error (malformed payload).",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation Error",
                    "error": {"code": "VALIDATION_ERROR", "details": None},
                    "detail": "Validation Error",
                    "errors": [
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


def _validate_reset_request_fields(body: PasswordResetRequest) -> None:
    """Validate business rules for the password reset request."""
    if body.terms_accepted is not True:
        raise BadRequestError(
            message="You must accept the Terms of Use and Privacy Policy.",
            code="TERMS_NOT_ACCEPTED",
            details={"field": "terms_accepted"},
        )


@router.post(
    "/api/password-recovery/reset",
    response_model=PasswordResetSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password using a valid token",
    description=(
        "Reset the user's password using a valid reset token from the email link. "
        "The new password must meet strength requirements and the Terms of Service "
        "and Privacy Policy must be accepted. The token is single-use and expires "
        "after 30 minutes. No authentication is required.\n\n"
        "**Request fields:** `token`, `password` (Reset My Password), "
        "`terms_accepted`.\n\n"
        "**Success (200):** returns user id, email, and UI guidance.\n\n"
        "**Errors:** weak password or terms not accepted → 400; "
        "expired token → 400 (`RESET_TOKEN_EXPIRED`); "
        "invalid/used token → 404 (`INVALID_RESET_TOKEN`)."
    ),
    responses=_RESET_PASSWORD_OPENAPI_RESPONSES,
    tags=["Password Recovery"],
)
async def reset_password(
    body: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Reset the user's password using a valid reset token.

    ``body: PasswordResetRequest`` is required so OpenAPI/Swagger exposes every
    ticket field (token, password, terms_accepted) in Try it out.
    """
    _validate_reset_request_fields(body)

    user = reset_password_with_token(
        db,
        token=body.token,
        password=body.password,
    )

    return {
        "success": True,
        "message": "Password reset successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "title": "Password updated",
            "message": "Your password has been reset successfully.",
            "description": "You can now sign in with your new password.",
            "link": "/sign-in",
        },
    }
