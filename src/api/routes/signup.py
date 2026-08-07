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
        if field == "email":
            raise BadRequestError(
                message="Invalid email format.",
                code="INVALID_EMAIL",
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
    tags=["User Management"],
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
                    "example": {
                        "success": False,
                        "message": "Invalid email format.",
                        "error": {
                            "code": "INVALID_EMAIL",
                            "details": {}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Unauthorized access.",
                        "error": {
                            "code": "UNAUTHORIZED",
                            "details": {}
                        }
                    }
                }
            }
        },
        403: {
            "description": "Forbidden access.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Forbidden access.",
                        "error": {
                            "code": "FORBIDDEN",
                            "details": {}
                        }
                    }
                }
            }
        },
        404: {
            "description": "Resource not found.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Resource not found.",
                        "error": {
                            "code": "NOT_FOUND",
                            "details": {}
                        }
                    }
                }
            }
        },
        409: {
            "description": "Conflict error, such as email already registered.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Email already registered.",
                        "error": {
                            "code": "EMAIL_ALREADY_REGISTERED",
                            "details": {}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Unprocessable entity, validation error.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation error.",
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "details": {}
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Internal server error.",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "details": {}
                        }
                    }
                }
            }
        }
    }
)
async def signup(request: Request, db: Session = Depends(get_db)):
    """Handle user signup."""
    signup_request = await _parse_signup_request(request)
    user, confirmation_link = create_user_with_confirmation(db, signup_request)
    return _build_signup_response(user, confirmation_link)
