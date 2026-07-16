from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.v1.schemas.admin import AdminUpdateUserRequest, AdminUpdateUserResponse
from src.api.v1.services.user_service import UserService
from src.database import get_db

router = APIRouter(prefix='/admin/users', tags=['admin'])


@router.post(
    '/update',
    response_model=AdminUpdateUserResponse,
    summary='Update user account status',
    description='Change a user account status to active, inactive, or suspended.',
    responses={
        400: {'description': 'Invalid user ID or account status'},
        500: {'description': 'Failed to update user account status'},
    },
)
async def admin_update_user(
    request: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
) -> AdminUpdateUserResponse:
    user_service = UserService(db)
    try:
        return user_service.update_user_account_status(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
