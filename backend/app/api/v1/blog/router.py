from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.middleware.auth import require_admin_role, require_user_role
from app.schemas.blog import (
    BlogCreateRequest,
    BlogListData,
    BlogListResponse,
    BlogResponse,
    BlogUpdateRequest,
)
from app.schemas.common import ErrorResponse
from app.services.blog_service import BlogService

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
                    "message": "Admin access required",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "Blog post not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Blog post not found",
                    "error": {"code": "BLOG_NOT_FOUND", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Duplicate blog post title",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "A blog post with this title already exists",
                    "error": {
                        "code": "BLOG_TITLE_ALREADY_EXISTS",
                        "details": None,
                    },
                }
            }
        },
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
    response_model=BlogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all blog posts",
    description=(
        "Retrieves all blog posts for the Blog screen. Requires an authenticated "
        "user with the **user** or **admin** role. Returns title, content, "
        "description, contact fields (first_name, last_name, email, phone), "
        "terms_accepted, and a link to each post's detail endpoint. "
        "Interactions are tracked via Google Analytics when configured."
    ),
    tags=["Blog"],
    responses={
        200: {
            "description": "Blog posts retrieved successfully",
            "model": BlogListResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def list_blog_posts(
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> BlogListResponse:
    """Return all blog posts for authenticated users."""
    service = BlogService(db)
    items = service.list_blog_posts(user_id=_user_id(current_user))
    return BlogListResponse(
        success=True,
        message="Blog posts retrieved successfully",
        data=BlogListData(items=items, total=len(items)),
    )


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post",
    description=(
        "Creates a new blog post using the Blog Details form fields: title, "
        "content, phone, terms_accepted, and optional contact information "
        "(first_name, last_name, email). Requires an authenticated user with "
        "the **admin** role. The `terms_accepted` field must be true. "
        "Duplicate titles return 409. Google Analytics tracks the creation "
        "event when configured."
    ),
    tags=["Blog"],
    responses={
        201: {
            "description": "Blog post created successfully",
            "model": BlogResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def create_blog_post(
    body: BlogCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> BlogResponse:
    """Create a new blog post (admin only)."""
    service = BlogService(db)
    blog_data = service.create_blog_post(body, user_id=_user_id(current_user))
    return BlogResponse(
        success=True,
        message="Blog post created successfully",
        data=blog_data,
    )


@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a blog post by ID",
    description=(
        "Retrieves a single blog post by UUID. Requires an authenticated user "
        "with the **user** or **admin** role. Returns all fields needed by the "
        "Blog Details screen including title, content, description, contact "
        "information, phone, terms_accepted, name, and link."
    ),
    tags=["Blog"],
    responses={
        200: {
            "description": "Blog post retrieved successfully",
            "model": BlogResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def get_blog_post(
    blog_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_user_role),
) -> BlogResponse:
    """Return a single blog post by ID."""
    service = BlogService(db)
    blog_data = service.get_blog_post(blog_id, user_id=_user_id(current_user))
    return BlogResponse(
        success=True,
        message="Blog post retrieved successfully",
        data=blog_data,
    )


@router.put(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a blog post",
    description=(
        "Updates an existing blog post by UUID. Accepts any subset of title, "
        "content, phone, terms_accepted, first_name, last_name, email, and "
        "description. Requires an authenticated user with the **admin** role. "
        "When `terms_accepted` is provided it must be true. Returns 404 when "
        "the blog post does not exist and 409 on duplicate title."
    ),
    tags=["Blog"],
    responses={
        200: {
            "description": "Blog post updated successfully",
            "model": BlogResponse,
        },
        **_COMMON_ERROR_RESPONSES,
    },
)
async def update_blog_post(
    blog_id: UUID,
    body: BlogUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> BlogResponse:
    """Update an existing blog post (admin only)."""
    service = BlogService(db)
    blog_data = service.update_blog_post(
        blog_id,
        body,
        user_id=_user_id(current_user),
    )
    return BlogResponse(
        success=True,
        message="Blog post updated successfully",
        data=blog_data,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog post",
    description=(
        "Permanently deletes a blog post by UUID. Requires an authenticated "
        "user with the **admin** role. Returns 204 with no body on success "
        "and 404 when the blog post does not exist. Google Analytics tracks "
        "the deletion event when configured."
    ),
    tags=["Blog"],
    responses={
        204: {"description": "Blog post deleted successfully"},
        **_COMMON_ERROR_RESPONSES,
    },
)
async def delete_blog_post(
    blog_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_admin_role),
) -> Response:
    """Delete a blog post (admin only)."""
    service = BlogService(db)
    service.delete_blog_post(blog_id, user_id=_user_id(current_user))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
