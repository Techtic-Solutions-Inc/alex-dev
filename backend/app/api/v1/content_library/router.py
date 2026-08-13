from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.auth import require_user_role
from app.schemas.common import ErrorResponse
from app.schemas.content_library import UserDetailsResponse
from app.services.content_library_service import ContentLibraryService

router = APIRouter()

_COMMON_ERROR_RESPONSES = {
    400: {
        "description": "Invalid input or validation failure",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation error",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "details": [
                            {
                                "field": "user_id",
                                "message": "value is not a valid uuid",
                            }
                        ],
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
        "description": (
            "Insufficient permissions or attempt to access another user's details"
        ),
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "examples": {
                    "forbidden_role": {
                        "summary": "Authenticated caller lacks a valid user role",
                        "value": {
                            "success": False,
                            "message": "Access denied",
                            "error": {"code": "FORBIDDEN", "details": None},
                        },
                    },
                    "other_user_details": {
                        "summary": "Caller requested a different user's details",
                        "value": {
                            "success": False,
                            "message": "You cannot access another user's details",
                            "error": {
                                "code": "USER_DETAILS_FORBIDDEN",
                                "details": None,
                            },
                        },
                    },
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
        "description": "Conflict (not applicable for this read endpoint)",
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


def _authenticated_user_id(current_user: dict[str, Any]) -> str:
    user_id = current_user.get("sub")
    if not user_id:
        raise UnauthorizedException(
            message="Invalid token payload",
            code="INVALID_TOKEN",
        )
    return str(user_id)


@router.get(
    "/user-details",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Content Library user details",
    description=(
        "Retrieves details for the **logged-in** user for the Content Library "
        "screen, including `user_id`, display `name` (first + last name), and "
        "`ai_credit_usage`.\n\n"
        "Authorization:\n"
        "- Requires a valid JWT access token with a user or admin role.\n"
        "- Returns only the authenticated user's own details."
    ),
    tags=["Content Library"],
    responses={**_COMMON_ERROR_RESPONSES},
    dependencies=[Depends(require_user_role)],
)
async def get_user_details(
    user_id: UUID | None = Query(
        default=None,
        description=(
            "Optional user UUID. When provided, must match the authenticated "
            "user; otherwise the API returns 403."
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    current_user: dict[str, Any] = Depends(require_user_role),
    db: Session = Depends(get_db),
) -> UserDetailsResponse:
    """
    Fetches the user details for the authenticated user.

    - **user_id**: Unique identifier for the user
    - **name**: User's display name
    - **ai_credit_usage**: AI credit usage details
    """
    service = ContentLibraryService(db)
    details = service.get_user_details(
        _authenticated_user_id(current_user),
        requested_user_id=str(user_id) if user_id is not None else None,
    )
    return UserDetailsResponse(
        success=True,
        message="User details retrieved successfully",
        data=details,
    )
