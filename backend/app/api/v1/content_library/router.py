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

@router.post("/templates", response_model=ContentTemplateResponse, responses=_COMMON_ERROR_RESPONSES)
async def create_content_template(
    body: ContentTemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserDetailsResponse = Depends(require_admin_role)
) -> Any:
    """
    Create a new content template.

    This endpoint allows an admin to create a new content template.
    """
    service = ContentLibraryService(db)
    return service.create_template(body)

@router.get("/templates", response_model=ContentTemplateListResponse, responses=_COMMON_ERROR_RESPONSES)
async def list_content_templates(
    db: Session = Depends(get_db),
    current_user: UserDetailsResponse = Depends(require_user_role)
) -> Any:
    """
    List content templates.

    This endpoint returns a list of content templates available to the user.
    """
    service = ContentLibraryService(db)
    return service.list_templates()

@router.put("/templates/{template_id}", response_model=ContentTemplateResponse, responses=_COMMON_ERROR_RESPONSES)
async def update_content_template(
    template_id: UUID,
    body: ContentTemplateUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserDetailsResponse = Depends(require_admin_role)
) -> Any:
    """
    Update a content template.

    This endpoint allows an admin to update an existing content template.
    """
    service = ContentLibraryService(db)
    return service.update_template(template_id, body)
