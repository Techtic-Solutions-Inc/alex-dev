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
        "description": "Resource not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Resource not found",
                    "error": {"code": "NOT_FOUND", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Conflict",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Conflict",
                    "error": {"code": "CONFLICT", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Validation error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation error",
                    "error": {"code": "VALIDATION_ERROR", "details": None},
                }
            }
        },
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


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description=(
        "Allows a user to change their password by providing the current password "
        "and a new password. The current password must be correct for the change "
        "to be successful."
    ),
    tags=["Profile"],
    operationId="changeUserPassword",
    responses={**_COMMON_ERROR_RESPONSES},
    dependencies=[Depends(require_user_role)],
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict[str, Any] = Depends(require_user_role),
    db: Session = Depends(get_db),
) -> ChangePasswordResponse:
    """
    Changes the password for the authenticated user.

    - **current_password**: The user's current password
    - **new_password**: The new password to set
    """
    auth_service = AuthService(db)
    return await auth_service.change_password(current_user, body)
