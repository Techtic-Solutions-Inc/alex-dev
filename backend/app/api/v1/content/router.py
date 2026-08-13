from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.middleware.auth import require_user_role
from app.schemas.common import ErrorResponse
from app.schemas.content import (
    ContentCreateRequest,
    ContentResponse,
    ContentUpdateRequest,
)
from app.services.content_service import ContentService

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
                                        "field": "caption",
                                        "message": "Field required",
                                    },
                                    {
                                        "field": "terms_accepted",
                                        "message": "Field required",
                                    },
                                ],
                            },
                        },
                    },
                    "empty_caption": {
                        "summary": "Empty caption on update",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "caption",
                                        "message": "This field cannot be empty",
                                    }
                                ],
                            },
                        },
                    },
                    "terms_not_accepted": {
                        "summary": "Terms checkbox not checked",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "terms_accepted",
                                        "message": (
                                            "You must accept the Terms of Use "
                                            "and Privacy Policy"
                                        ),
                                    }
                                ],
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
        "description": "Content not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Content not found",
                    "error": {"code": "CONTENT_NOT_FOUND", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Duplicate content caption",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Content with this caption already exists",
                    "error": {
                        "code": "CONTENT_CAPTION_ALREADY_EXISTS",
                        "details": None,
                    },
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


def _user_id(current_user: dict[str, Any]) -> str | None:
    return str(current_user.get("sub")) if current_user.get("sub") else None


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create content details",
    description=(
        "Creates new content details for the Real Estate Professional Content "
        "Details screen. Accepts Figma form fields: `caption`, `terms_accepted` "
        "(Privacy Policy), `privacy_policy`, and `phone` (Mobile App Development), "
        "plus optional `full_name` and `description`. Requires an authenticated "
        "user. Duplicate captions return 409. Missing required fields return 400. "
        "Interactions are tracked via Google Analytics and Stripe when configured."
    ),
    tags=["Content"],
    responses={
        201: {
            "description": "Content created successfully",
            "model": ContentResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def create_content(
    body: ContentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ContentResponse:
    """Create new content details (authenticated users only)."""
    service = ContentService(db)
    content_data = service.create_content(body, user_id=_user_id(current_user))
    return ContentResponse(
        success=True,
        message="Content created successfully",
        data=content_data,
    )


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get content details by ID",
    description=(
        "Retrieves content details by UUID. This endpoint is **public** — no "
        "authentication is required. Returns caption, phone, terms_accepted, "
        "privacy_policy, full_name, description, link, and error fields used by "
        "the Content Calendar / Content Details screens. Returns 404 when the "
        "content does not exist."
    ),
    tags=["Content"],
    responses={
        200: {
            "description": "Content retrieved successfully",
            "model": ContentResponse,
        },
        **{k: v for k, v in _COMMON_ERROR_RESPONSES.items() if k != 401},
    },
)
async def get_content(
    content_id: UUID,
    db: Session = Depends(get_db),
) -> ContentResponse:
    """Return content details by ID (public)."""
    service = ContentService(db)
    content_data = service.get_content(content_id)
    return ContentResponse(
        success=True,
        message="Content retrieved successfully",
        data=content_data,
    )


@router.put(
    "/{content_id}",
    response_model=ContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update content details",
    description=(
        "Updates existing content details by UUID. Accepts any subset of "
        "`caption`, `terms_accepted`, `privacy_policy`, `phone`, `full_name`, "
        "and `description`. Requires an authenticated user. Empty caption "
        "returns 400. Duplicate captions return 409. Returns 404 when the "
        "content does not exist. Google Analytics and Stripe track the update "
        "when configured."
    ),
    tags=["Content"],
    responses={
        200: {
            "description": "Content updated successfully",
            "model": ContentResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def update_content(
    content_id: UUID,
    body: ContentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ContentResponse:
    """Update existing content details (authenticated users only)."""
    service = ContentService(db)
    content_data = service.update_content(
        content_id,
        body,
        user_id=_user_id(current_user),
    )
    return ContentResponse(
        success=True,
        message="Content updated successfully",
        data=content_data,
    )
