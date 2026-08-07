"""User registration and email confirmation routes."""

import json

from fastapi import APIRouter, Depends, Query, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.api.services.user_service import (
    confirm_user_email,
    create_user_with_confirmation,
    validate_signup_required_fields,
)
from src.config.database import get_db
from src.config.settings import get_settings
from src.exceptions import BadRequestError
from src.schemas.auth import (
    ConfirmEmailSuccessResponse,
    SignupRequest,
    SignupSuccessResponse,
)

settings = get_settings()
router = APIRouter()


def _build_signup_response(user, confirmation_link: str) -> dict:
    """Build the signup success payload for the frontend."""
    link = confirmation_link if settings.environment != "production" else None
    full_name = f"{user.first_name} {user.last_name}".strip()

    return {
        "success": True,
        "message": "Account created successfully. Please confirm your email.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "name": full_name,
            "title": "Account created",
            "message": "Please check your email to confirm your account.",
            "description": (
                "We sent a confirmation email to your inbox. "
                "Click the link in that email to activate your account."
            ),
            "link": link,
            "redirect": "/sign-in",
        },
    }


async def _parse_signup_request(request: Request) -> SignupRequest:
    """Parse and validate the signup request body."""
    try:
        raw_body = await request.body()
        body = json.loads(raw_body) if raw_body else {}
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BadRequestError(
            message="Invalid request body.",
            code="INVALID_REQUEST_BODY",
        ) from exc

    validate_signup_required_fields(body)

    try:
        return SignupRequest.model_validate(body)
    except ValidationError as exc:
        first_error = exc.errors()[0]
        field = ".".join(str(part) for part in first_error.get("loc", ()))
        message = first_error.get("msg", "Invalid value")
        if field == "password":
            raise BadRequestError(
                message=message,
                code="WEAK_PASSWORD",
                details={"field": "password"},
            ) from exc
        raise BadRequestError(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field or "body"},
        ) from exc


@router.post(
    "/api/auth/signup",
    response_model=SignupSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Create a new user account with first name, last name, email address, "
        "password, and terms acceptance. The email must be unique and the password "
        "must meet strength requirements. Terms of Use and Privacy Policy must be "
        "accepted before registration. Upon successful registration, a confirmation "
        "email is sent via SendGrid. No authentication is required."
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
                            "email": "john.doe@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "name": "John Doe",
                            "title": "Account created",
                            "message": "Please check your email to confirm your account.",
                            "description": (
                                "We sent a confirmation email to your inbox. "
                                "Click the link in that email to activate your account."
                            ),
                            "link": None,
                            "redirect": "/sign-in",
                        },
                    }
                }
            },
        },
        400: {
            "description": (
                "Invalid input such as missing name fields, invalid email format, "
                "weak password, or terms not accepted."
            ),
            "content": {
                "application/json": {
                    "examples": {
                        "missing_first_name": {
                            "summary": "Missing first name",
                            "value": {
                                "success": False,
                                "message": "First name is required.",
                                "error": {
                                    "code": "MISSING_FIRST_NAME",
                                    "details": {"field": "first_name"},
                                },
                            },
                        },
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
                        "terms_not_accepted": {
                            "summary": "Terms of Use not accepted",
                            "value": {
                                "success": False,
                                "message": (
                                    "You must accept the Terms of Use and "
                                    "Privacy Policy."
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
    tags=["Authentication"],
)
async def signup(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Register a new user and send a confirmation email."""
    signup_request = await _parse_signup_request(request)

    user, confirmation_link = create_user_with_confirmation(
        db,
        first_name=signup_request.first_name,
        last_name=signup_request.last_name,
        email=signup_request.email,
        password=signup_request.password,
    )

    return _build_signup_response(user, confirmation_link)


@router.get(
    "/api/auth/confirm-email",
    response_model=ConfirmEmailSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a user's email address",
    description=(
        "Verify a user's email address using the token sent in the confirmation email. "
        "The token is single-use and expires after the configured verification window. "
        "No authentication is required."
    ),
    responses={
        200: {
            "description": "Email confirmed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Email confirmed successfully.",
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "title": "Email confirmed",
                            "message": "Your email address has been verified.",
                            "description": "You can now sign in to your account.",
                            "link": "/sign-in",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid, expired, or already used confirmation token.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "Missing token",
                            "value": {
                                "success": False,
                                "message": "A confirmation token is required.",
                                "error": {"code": "INVALID_TOKEN", "details": None},
                            },
                        },
                        "expired_token": {
                            "summary": "Expired token",
                            "value": {
                                "success": False,
                                "message": (
                                    "The confirmation link has expired. "
                                    "Please sign up again."
                                ),
                                "error": {
                                    "code": "CONFIRMATION_TOKEN_EXPIRED",
                                    "details": None,
                                },
                            },
                        },
                    }
                }
            },
        },
        404: {
            "description": "Confirmation token not found.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": (
                            "The confirmation link is invalid or has already been used."
                        ),
                        "error": {
                            "code": "INVALID_CONFIRMATION_TOKEN",
                            "details": None,
                        },
                    }
                }
            },
        },
        422: {
            "description": "Missing query parameter.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation Error",
                        "error": {"code": "VALIDATION_ERROR", "details": None},
                        "detail": "Validation Error",
                        "errors": [
                            {"field": "token", "message": "Field required"},
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
    tags=["Authentication"],
)
def confirm_email(
    token: str = Query(
        ...,
        min_length=1,
        description="Email verification token from the confirmation email.",
        examples=["abc123def456"],
    ),
    db: Session = Depends(get_db),
) -> dict:
    """Confirm a user's email address."""
    user = confirm_user_email(db, token=token)

    return {
        "success": True,
        "message": "Email confirmed successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "title": "Email confirmed",
            "message": "Your email address has been verified.",
            "description": "You can now sign in to your account.",
            "link": "/sign-in",
        },
    }
