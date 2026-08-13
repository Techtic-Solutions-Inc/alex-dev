from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.auth import require_admin_role, require_user_role
from app.schemas.common import ErrorResponse
from app.schemas.content_library import (
    ContentTemplateCreateRequest,
    ContentTemplateListData,
    ContentTemplateListResponse,
    ContentTemplateResponse,
    ContentTemplateUpdateRequest,
    UserDetailsResponse,
)
from app.services.content_library_service import ContentLibraryService

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
                                        "message": "Title is required",
                                    }
                                ],
                            },
                        },
                    },
                    "invalid_search_query": {
                        "summary": "Empty or invalid search query",
                        "value": {
                            "success": False,
                            "message": "Search query is required",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "q",
                                        "message": "Search query must not be empty",
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
                "examples": {
                    "forbidden_role": {
                        "summary": "Authenticated caller lacks a valid user role",
                        "value": {
                            "success": False,
                            "message": "Access denied",
                            "error": {"code": "FORBIDDEN", "details": None},
                        },
                    },
                    "admin_required": {
                        "summary": "Admin role required for write operations",
                        "value": {
                            "success": False,
                            "message": "Admin access required",
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
        "description": "Resource not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "examples": {
                    "template_not_found": {
                        "summary": "Content template not found",
                        "value": {
                            "success": False,
                            "message": "Content template not found",
                            "error": {
                                "code": "CONTENT_TEMPLATE_NOT_FOUND",
                                "details": None,
                            },
                        },
                    },
                    "user_not_found": {
                        "summary": "User not found",
                        "value": {
                            "success": False,
                            "message": "User not found",
                            "error": {"code": "USER_NOT_FOUND", "details": None},
                        },
                    },
                }
            }
        },
    },
    409: {
        "description": "Duplicate content template title",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "A content template with this title already exists",
                    "error": {
                        "code": "CONTENT_TEMPLATE_TITLE_ALREADY_EXISTS",
                        "details": None,
                    },
                }
            }
        },
    },
    422: {
        "description": "Validation error (mapped to 400)",
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


def _optional_user_id(current_user: dict[str, Any]) -> str | None:
    user_id = current_user.get("sub")
    return str(user_id) if user_id else None


@router.get(
    "",
    response_model=ContentTemplateListResponse,
    status_code=status.HTTP_200_OK,
    summary="List active content templates",
    description=(
        "Retrieves a paginated list of **active** content templates for the "
        "Content Library screen. This endpoint is **public** — no authentication "
        "is required. Only templates with `status` set to `active` are returned."
    ),
    tags=["Content Library"],
    responses={
        200: {
            "description": "Content templates retrieved successfully",
            "model": ContentTemplateListResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def list_content_templates(
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
        description="Maximum number of templates per page",
        examples=[20],
    ),
    db: Session = Depends(get_db),
) -> ContentTemplateListResponse:
    """Return paginated active content templates (public)."""
    service = ContentLibraryService(db)
    items, total = service.list_content_templates(page=page, limit=limit)
    return ContentTemplateListResponse(
        success=True,
        message="Content templates retrieved successfully",
        data=ContentTemplateListData(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
    )


@router.get(
    "/search",
    response_model=ContentTemplateListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search active content templates",
    description=(
        "Searches **active** content templates by title or description using the "
        "`q` query parameter. Requires an authenticated user with the **user** or "
        "**admin** role. Returns paginated results. Empty or whitespace-only search "
        "queries return 400."
    ),
    tags=["Content Library"],
    responses={
        200: {
            "description": "Search results retrieved successfully",
            "model": ContentTemplateListResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
    dependencies=[Depends(require_user_role)],
)
async def search_content_templates(
    q: str = Query(
        ...,
        min_length=1,
        max_length=255,
        description="Search query matched against title and description",
        examples=["open house"],
    ),
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
        description="Maximum number of templates per page",
        examples=[20],
    ),
    current_user: dict[str, Any] = Depends(require_user_role),
    db: Session = Depends(get_db),
) -> ContentTemplateListResponse:
    """Search active content templates (authenticated users)."""
    service = ContentLibraryService(db)
    items, total = service.search_content_templates(
        q,
        page=page,
        limit=limit,
        user_id=_optional_user_id(current_user),
    )
    return ContentTemplateListResponse(
        success=True,
        message="Content templates retrieved successfully",
        data=ContentTemplateListData(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
    )


@router.post(
    "",
    response_model=ContentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a content template",
    description=(
        "Creates a new content template with `title`, optional `description`, "
        "and `status` (`active` or `inactive`). Requires an authenticated user "
        "with the **admin** role. Duplicate titles return 409."
    ),
    tags=["Content Library"],
    responses={
        201: {
            "description": "Content template created successfully",
            "model": ContentTemplateResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def create_content_template(
    body: ContentTemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> ContentTemplateResponse:
    """Create a new content template (admin only)."""
    service = ContentLibraryService(db)
    template_data = service.create_content_template(
        body,
        user_id=_optional_user_id(current_user),
    )
    return ContentTemplateResponse(
        success=True,
        message="Content template created successfully",
        data=template_data,
    )


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
    """Fetch user details for the authenticated user."""
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


@router.get(
    "/{template_id}",
    response_model=ContentTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a content template by ID",
    description=(
        "Retrieves detailed information about a specific content template by "
        "UUID. Requires an authenticated user with the **user** or **admin** "
        "role. Returns `id`, `title`, `description`, and `status`."
    ),
    tags=["Content Library"],
    responses={
        200: {
            "description": "Content template retrieved successfully",
            "model": ContentTemplateResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def get_content_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> ContentTemplateResponse:
    """Return a single content template by ID (authenticated users)."""
    service = ContentLibraryService(db)
    template_data = service.get_content_template(
        template_id,
        user_id=_optional_user_id(current_user),
    )
    return ContentTemplateResponse(
        success=True,
        message="Content template retrieved successfully",
        data=template_data,
    )


@router.put(
    "/{template_id}",
    response_model=ContentTemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a content template",
    description=(
        "Updates an existing content template by UUID. Accepts any subset of "
        "`title`, `description`, and `status`. Requires an authenticated user "
        "with the **admin** role. Returns 404 when the template does not exist "
        "and 409 on duplicate title."
    ),
    tags=["Content Library"],
    responses={
        200: {
            "description": "Content template updated successfully",
            "model": ContentTemplateResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def update_content_template(
    template_id: UUID,
    body: ContentTemplateUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> ContentTemplateResponse:
    """Update an existing content template (admin only)."""
    service = ContentLibraryService(db)
    template_data = service.update_content_template(
        template_id,
        body,
        user_id=_optional_user_id(current_user),
    )
    return ContentTemplateResponse(
        success=True,
        message="Content template updated successfully",
        data=template_data,
    )


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a content template",
    description=(
        "Permanently deletes a content template by UUID. Requires an "
        "authenticated user with the **admin** role. Returns 204 with no body "
        "on success and 404 when the template does not exist."
    ),
    tags=["Content Library"],
    responses={
        204: {"description": "Content template deleted successfully"},
        **_COMMON_ERROR_RESPONSES,
    },
)
async def delete_content_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> Response:
    """Delete a content template (admin only)."""
    service = ContentLibraryService(db)
    service.delete_content_template(
        template_id,
        user_id=_optional_user_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
