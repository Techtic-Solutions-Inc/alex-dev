from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.middleware.auth import require_admin_role, require_user_role
from app.schemas.announcement import (
    AnnouncementCreateRequest,
    AnnouncementListData,
    AnnouncementListResponse,
    AnnouncementResponse,
    AnnouncementUpdateRequest,
)
from app.schemas.common import ErrorResponse
from app.services.announcement_service import AnnouncementService

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
                                        "field": "title",
                                        "message": "Field required",
                                    }
                                ],
                            },
                        },
                    },
                    "privacy_policy_not_accepted": {
                        "summary": "Privacy Policy checkbox not checked",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "privacy_policy_accepted",
                                        "message": "You must accept the Privacy Policy",
                                    }
                                ],
                            },
                        },
                    },
                    "terms_not_accepted": {
                        "summary": "Terms of Service checkbox not checked",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "terms_of_service_accepted",
                                        "message": (
                                            "You must accept the Terms of Service"
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
                    "message": "Admin access required",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "Announcement not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Announcement not found",
                    "error": {"code": "ANNOUNCEMENT_NOT_FOUND", "details": None},
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
}


def _user_id(current_user: dict[str, Any]) -> str | None:
    return str(current_user.get("sub")) if current_user.get("sub") else None


@router.get(
    "",
    response_model=AnnouncementListResponse,
    status_code=status.HTTP_200_OK,
    summary="List announcements",
    description=(
        "Retrieves a paginated list of announcements for the Dashboard "
        "Announcements screen. Requires an authenticated user with the "
        "**user** or **admin** role. Returns title, body, highlights, and "
        "consent flags for each announcement. Supports optional filtering by "
        "creation date (`date` query parameter in YYYY-MM-DD format)."
    ),
    tags=["Announcements"],
    responses={
        200: {
            "description": "Announcements retrieved successfully",
            "model": AnnouncementListResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def list_announcements(
    page: int = Query(
        1,
        ge=1,
        description="Page number (1-based)",
        examples=[1],
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of announcements per page",
        examples=[20],
    ),
    filter_date: date | None = Query(
        None,
        alias="date",
        description=(
            "Filter announcements by creation date (YYYY-MM-DD). "
            "Only announcements created on this date are returned."
        ),
        examples=["2026-08-13"],
    ),
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> AnnouncementListResponse:
    """Return a paginated list of announcements."""
    service = AnnouncementService(db)
    items, total = service.list_announcements(
        page=page,
        limit=limit,
        filter_date=filter_date,
        user_id=_user_id(current_user),
    )
    return AnnouncementListResponse(
        success=True,
        message="Announcements retrieved successfully",
        data=AnnouncementListData(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
    )


@router.post(
    "",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new announcement",
    description=(
        "Creates a new announcement for the Announcement screen using title, body, "
        "highlights, and consent checkboxes (`privacy_policy_accepted`, "
        "`terms_of_service_accepted`). Requires an authenticated user with the "
        "**admin** role. Both consent fields must be true."
    ),
    tags=["Announcements"],
    responses={
        201: {
            "description": "Announcement created successfully",
            "model": AnnouncementResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def create_announcement(
    body: AnnouncementCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> AnnouncementResponse:
    """Create a new announcement (admin only)."""
    service = AnnouncementService(db)
    announcement_data = service.create_announcement(
        body,
        user_id=_user_id(current_user),
    )
    return AnnouncementResponse(
        success=True,
        message="Announcement created successfully",
        data=announcement_data,
    )


@router.get(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an announcement by ID",
    description=(
        "Retrieves a single announcement by UUID. Requires an authenticated user "
        "with the **user** or **admin** role. Returns title, body, highlights, "
        "and consent flags."
    ),
    tags=["Announcements"],
    responses={
        200: {
            "description": "Announcement retrieved successfully",
            "model": AnnouncementResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def get_announcement(
    announcement_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> AnnouncementResponse:
    """Return a single announcement by ID."""
    service = AnnouncementService(db)
    announcement_data = service.get_announcement(
        announcement_id,
        user_id=_user_id(current_user),
    )
    return AnnouncementResponse(
        success=True,
        message="Announcement retrieved successfully",
        data=announcement_data,
    )


@router.put(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an announcement",
    description=(
        "Updates an existing announcement by UUID. Accepts any subset of title, "
        "body, highlights, `privacy_policy_accepted`, and "
        "`terms_of_service_accepted`. Requires an authenticated user with the "
        "**admin** role. When consent fields are provided they must "
        "be true. Returns 404 when the announcement does not exist."
    ),
    tags=["Announcements"],
    responses={
        200: {
            "description": "Announcement updated successfully",
            "model": AnnouncementResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def update_announcement(
    announcement_id: UUID,
    body: AnnouncementUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> AnnouncementResponse:
    """Update an existing announcement (admin only)."""
    service = AnnouncementService(db)
    announcement_data = service.update_announcement(
        announcement_id,
        body,
        user_id=_user_id(current_user),
    )
    return AnnouncementResponse(
        success=True,
        message="Announcement updated successfully",
        data=announcement_data,
    )


@router.delete(
    "/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an announcement",
    description=(
        "Permanently deletes an announcement by UUID. Requires an authenticated "
        "user with the **admin** role. Returns 204 with no body on "
        "success and 404 when the announcement does not exist."
    ),
    tags=["Announcements"],
    responses={
        204: {"description": "Announcement deleted successfully"},
        **_COMMON_ERROR_RESPONSES,
    },
)
async def delete_announcement(
    announcement_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> Response:
    """Delete an announcement (admin only)."""
    service = AnnouncementService(db)
    service.delete_announcement(
        announcement_id,
        user_id=_user_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
