from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.api.v1.schemas.auth import ResetPasswordRequest, ResetPasswordResponse
from src.api.v1.services.auth_service import AuthService
from src.config import settings
from src.database import get_db

router = APIRouter(tags=['auth'])


@router.get(
    '/reset-password',
    summary='Validate reset link and redirect to password reset page',
    responses={
        400: {'description': 'Invalid or expired reset link'},
    },
)
async def redirect_to_reset_password_page(
    token: str = Query(..., description='Password reset token from email link'),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    auth_service = AuthService(db)
    try:
        auth_service.validate_reset_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    redirect_url = f'{settings.PASSWORD_RESET_FRONTEND_URL}?token={token}'
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post(
    '/reset-password',
    response_model=ResetPasswordResponse,
    summary='Reset user password',
    description='Validate the reset token and update the user password.',
    responses={
        400: {'description': 'Invalid input, password mismatch, or invalid reset link'},
    },
)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    auth_service = AuthService(db)
    try:
        return await auth_service.reset_password(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
