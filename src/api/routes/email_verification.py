"""Email verification routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.services.user_service import (
    request_email_verification,
    validate_email_verification_request_fields,
)
from src.config.database import get_db
from src.config.settings import get_settings
from src.schemas.email_verification import (
    EmailVerificationRequest,
    EmailVerificationSuccessResponse,
)

settings = get_settings()
router = APIRouter()


def _build_verification_response(user, verification_link: str) -> dict:
    """Build the email verification success payload for the frontend."""
    link = verification_link if settings.environment != "production" else None

    return {
        "success": True,
        "message": "Verification email sent successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "address": user.email,
            "title": "Verify your email address",
            "message": "We sent a verification link to your email.",
            "description": (
                "This verification link will expire in 24 hours. If you didn't create "
                "an account on Agentwise, you can safely ignore this email."
            ),
            "link": link,
        },
    }


_EMAIL_VERIFY_OPENAPI_RESPONSES = {
    201: {
        "description": "Verification email sent successfully.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Verification email sent successfully.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "first_name": "John",
                        "address": "user@example.com",
                        "title": "Verify your email address",
                        "message": "We sent a verification link to your email.",
                        "description": (
                            "This verification link will expire in 24 hours. If you "
                            "didn't create an account on Agentwise, you can safely "
                            "ignore this email."
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
        "description": "Not applicable — email verification is a public endpoint.",
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
        "description": "Not applicable — email verification is a public endpoint.",
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
        "description": "No account found for the provided email address.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "No account was found for this email address.",
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "details": {"field": "email"},
                    },
                }
            }
        },
    },
    409: {
        "description": "Email address is already verified or in use by another account.",
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
    "/api/email/verify",
    response_model=EmailVerificationSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send an email verification link",
    description=(
        "Request a verification email for the provided email address. The email must "
        "belong to an existing unverified account. Terms of Service and Privacy Policy "
        "must be accepted before the email is sent. A verification link is delivered "
        "via SendGrid and expires after the configured verification window (24 hours "
        "by default). No authentication is required.\n\n"
        "**Request fields:** `email`, `terms_accepted`.\n\n"
        "**Success (201):** returns the user id, email, first name, address, UI "
        "guidance (`title`, `message`, `description`, `link`).\n\n"
        "**Errors:** invalid/missing email or terms not accepted → 400 with stable "
        "codes (`EMPTY_EMAIL`, `INVALID_EMAIL`, `TERMS_NOT_ACCEPTED`); no matching "
        "account → 404 (`USER_NOT_FOUND`); email already verified → 409 "
        "(`EMAIL_ALREADY_EXISTS`)."
    ),
    responses=_EMAIL_VERIFY_OPENAPI_RESPONSES,
    tags=["Email Verification"],
)
async def verify_email(
    body: EmailVerificationRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Send a verification email for an unverified account.

    ``body: EmailVerificationRequest`` is required so OpenAPI/Swagger exposes every
    ticket field (email, terms_accepted) in Try it out.
    """
    validate_email_verification_request_fields(body.model_dump())

    user, verification_link = request_email_verification(db, email=body.email)

    return _build_verification_response(user, verification_link)
