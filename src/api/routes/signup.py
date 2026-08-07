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
        "Create a new user account with email and password. "
        "The user will receive a confirmation email to activate their account. "
        "Ensure all required fields are provided and valid."
    ),
    tags=["User Registration"],
    operationId="registerUser",
    responses={
        201: {
            "description": "User account created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Account created successfully. Please confirm your email.",
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "name": "John Doe",
                            "title": "Account created",
                            "message": "Please check your email to confirm your account.",
                            "description": "We sent a confirmation email to your inbox. Click the link in that email to activate your account.",
                            "link": "http://example.com/confirm?token=abc123",
                            "redirect": "/sign-in",
                        },
                    }
                }
            }
        },
        400: {
            "description": "Invalid request body or missing required fields.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid request body.",
                        "error": {"code": "INVALID_REQUEST_BODY", "details": None},
                    }
                }
            }
        },
        422: {
            "description": "Validation error for one or more fields.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation error.",
                        "error": {"code": "VALIDATION_ERROR", "details": {"field": "email"}},
                    }
                }
            }
        },
    },
)
async def signup(
    request: Request,
    db: Session = Depends(get_db),
) -> SignupSuccessResponse:
    """Register a new user and send confirmation email."""
    signup_request = await _parse_signup_request(request)
    user, confirmation_link = create_user_with_confirmation(db, signup_request)
    return _build_signup_response(user, confirmation_link)
