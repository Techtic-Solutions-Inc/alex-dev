from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.config.settings import PASSWORD_RESET_FRONTEND_URL
from src.database import get_db
from src.models.user import User
from src.schemas.auth import ResetPasswordRequest, ResetPasswordResponse
from src.utils.logger import logger

router = APIRouter()


def _validate_reset_token(db: Session, token: str) -> User:
    user = User.get_by_reset_token(db, token)
    if user is None or not user.is_reset_token_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    return user


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
    logger.info("Password reset link validation attempt")
    _validate_reset_token(db, token)
    redirect_url = f"{PASSWORD_RESET_FRONTEND_URL}?token={token}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Reset user password",
    description=(
        "Reset a user's password using a valid reset token. "
        "The new password and confirmation must match."
    ),
    responses={
        400: {"description": "Invalid input, password mismatch, or invalid reset link"},
    },
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ResetPasswordResponse:
    """Validate the reset link, check password match, and update the user's password."""
    logger.info("Password reset attempt")

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    user = _validate_reset_token(db, request.token)
    user.update_password(request.new_password)
    db.commit()

    logger.info("Password reset successful for user_id=%s", user.id)
    return ResetPasswordResponse()
