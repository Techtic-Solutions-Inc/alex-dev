from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.auth import require_user_role
from app.schemas.common import ErrorResponse
from app.schemas.profile import (
    ChangePasswordData,
    ChangePasswordRequest,
    ChangePasswordResponse,
    ProfileData,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.auth_service import AuthService

router = APIRouter()

_COMMON_ERROR_RESPONSES = {
    400: {
        "description": "Invalid input or validation failure",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "examples": {
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
                                    },
                                    {
                                        "field": "email",
                                        "message": "Field required",
                                    },
                                ],
                            },
                        },
                    },
                    "incorrect_current_password": {
                        "summary": "Current password is incorrect",
                        "value": {
                            "success": False,
                            "message": "Current password is incorrect",
                            "error": {
                                "code": "INCORRECT_CURRENT_PASSWORD",
                                "details": None,
                            },
                        },
                    },
                    "email_already_exists": {
                        "summary": "Email already registered to another account",
                        "value": {
                            "success": False,
                            "message": "An account with this email already exists",
                            "error": {
                                "code": "EMAIL_ALREADY_EXISTS",
                                "details": None,
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Authentication required",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication required",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            }
        },
    },
    403: {
        "description": "Insufficient permissions",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Access denied",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "User not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "User not found",
                    "error": {"code": "USER_NOT_FOUND", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Resource conflict (not typically returned by profile endpoints)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Resource conflict",
                    "error": {"code": "CONFLICT", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Validation error (not applicable; mapped to 400)",
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
}


def _user_id(current_user: dict[str, Any]) -> str:
    user_id = current_user.get("sub")
    if not user_id:
        raise UnauthorizedException(
            message="Invalid token payload",
            code="INVALID_TOKEN",
        )
    return str(user_id)


@router.get(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Returns the authenticated user's profile data for the Profile screen, "
        "including `first_name`, `last_name`, `email`, `mobile_number`, `bio`, "
        "nested `address` (`street`, `city`, `state`, `zip`, `country`), and "
        "`time_zone`. Requires a valid JWT access token. Unauthenticated "
        "requests receive 401."
    ),
    tags=["Profile"],
    responses={
        200: {
            "description": "Profile retrieved successfully",
            "model": ProfileResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Profile retrieved successfully",
                        "data": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john.doe@example.com",
                            "mobile_number": "1234567890",
                            "bio": "This is my bio.",
                            "address": {
                                "street": "123 Main St",
                                "city": "Anytown",
                                "state": "CA",
                                "zip": "12345",
                                "country": "USA",
                            },
                            "time_zone": "GMT-4",
                        },
                    }
                }
            },
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ProfileResponse:
    """Fetch the authenticated user's profile."""
    service = AuthService(db)
    user = service.get_profile(_user_id(current_user))
    return ProfileResponse(
        success=True,
        message="Profile retrieved successfully",
        data=ProfileData.from_user(user),
    )


@router.put(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Updates the authenticated user's profile information from the Profile "
        "form. Required body fields: `first_name`, `last_name`, `email`, "
        "`mobile_number`, `bio`, `address` (with `street`, `city`, `state`, "
        "`zip`, `country`), and `time_zone`. Missing or invalid fields return "
        "400 with field-level details. Duplicate email returns 400 "
        "(`EMAIL_ALREADY_EXISTS`). Requires authentication; unauthenticated "
        "requests receive 401."
    ),
    tags=["Profile"],
    responses={
        200: {
            "description": "Profile updated successfully",
            "model": ProfileResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Profile updated successfully",
                        "data": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john.doe@example.com",
                            "mobile_number": "1234567890",
                            "bio": "This is my bio.",
                            "address": {
                                "street": "123 Main St",
                                "city": "Anytown",
                                "state": "CA",
                                "zip": "12345",
                                "country": "USA",
                            },
                            "time_zone": "GMT-4",
                        },
                    }
                }
            },
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def update_profile(
    body: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ProfileResponse:
    """Update the authenticated user's profile."""
    service = AuthService(db)
    user = service.update_profile(_user_id(current_user), body)
    return ProfileResponse(
        success=True,
        message="Profile updated successfully",
        data=ProfileData.from_user(user),
    )


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Change current user password",
    description=(
        "Changes the authenticated user's password. Requires `current_password` "
        "and `new_password` in the request body. The new password must be at "
        "least 8 characters and contain at least one letter and one number. "
        "An incorrect current password returns 400 "
        "(`INCORRECT_CURRENT_PASSWORD`). Only the authenticated user can change "
        "their own password. Unauthenticated requests receive 401."
    ),
    tags=["Profile"],
    responses={
        200: {
            "description": "Password changed successfully",
            "model": ChangePasswordResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Password changed successfully",
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                        },
                    }
                }
            },
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ChangePasswordResponse:
    """Change the authenticated user's password."""
    service = AuthService(db)
    user = service.change_password(_user_id(current_user), body)
    return ChangePasswordResponse(
        success=True,
        message="Password changed successfully",
        data=ChangePasswordData(id=str(user.id)),
    )
