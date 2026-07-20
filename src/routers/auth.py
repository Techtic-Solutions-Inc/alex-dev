from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database import get_db
from src.schemas.auth import ResetPasswordRequest, ResetPasswordResponse
from src.services import auth as auth_service

router = APIRouter(tags=["auth"])


@router.get(
    "/reset-password",
    summary="Validate reset link and redirect to password reset page",
    responses={
        302: {"description": "Redirect to password reset page"},
        400: {"description": "Invalid or expired reset link"},
    },
)
def redirect_to_reset_password_page(
    token: str = Query(..., min_length=1, description="Password reset token from email link"),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Validate the reset link and redirect the user to the password reset page."""
    try:
        auth_service.validate_reset_token(db, token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    redirect_url = f"{settings.PASSWORD_RESET_FRONTEND_URL}?token={token}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Reset user password",
    responses={
        400: {"description": "Invalid input, password mismatch, or invalid reset link"},
    },
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    """Reset the user's password using a valid reset token."""
    try:
        return auth_service.reset_password(db, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
