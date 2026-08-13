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
from app.schemas.blog_details import (
    BlogDetailsGetResponse,
    BlogDetailsSubmissionResponse,
    BlogDetailsSubmitRequest,
    BlogDetailsUpdateRequest,
)
from app.schemas.common import ErrorResponse
from app.services.blog_detail_service import BlogDetailService
from app.services.blog_service import BlogService

router = APIRouter()

@router.post("/details", response_model=BlogDetailsSubmissionResponse, responses=_COMMON_ERROR_RESPONSES)
async def submit_blog_details(
    body: BlogDetailsSubmitRequest,
    db: Session = Depends(get_db),
    current_user: UserDetailsResponse = Depends(require_user_role)
) -> Any:
    """
    Submit blog details.

    This endpoint allows a user to submit details for a blog.
    """
    service = BlogDetailService(db)
    return service.submit_details(body)

@router.get("/details/{blog_id}", response_model=BlogDetailsGetResponse, responses=_COMMON_ERROR_RESPONSES)
async def get_blog_details(
    blog_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserDetailsResponse = Depends(require_user_role)
) -> Any:
    """
    Get blog details.

    This endpoint retrieves the details of a specific blog by its ID.
    """
    service = BlogDetailService(db)
    return service.get_details(blog_id)
