from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.auth import (
    ExpiredTokenResponse,
    ResetPasswordRequest,
    ResetPasswordTokenResponse,
)
from src.services.password_reset_service import (
    EXPIRED_TOKEN_MESSAGE,
    INVALID_TOKEN_MESSAGE,
    PASSWORD_RESET_REQUEST_PATH,
    InvalidTokenError,
    TokenExpiredError,
    reset_password,
    validate_password_reset_token,
)
from src.utils.logger import logger

router = APIRouter(prefix="/auth")


def _expired_redirect() -> RedirectResponse:
    message = quote(EXPIRED_TOKEN_MESSAGE)
    return RedirectResponse(
        url=f"{PASSWORD_RESET_REQUEST_PATH}?message={message}",
        status_code=302,
    )


@router.get(
    "/reset-password",
    response_model=ResetPasswordTokenResponse,
    summary="Validate password reset token",
    description=(
        "Validate a password reset token when the user opens the reset link. "
        "Redirects to the password reset request page if the token has expired."
    ),
    responses={
        302: {"description": "Token expired; redirected to password reset request page"},
        400: {"description": "Invalid reset link"},
    },
)
async def validate_reset_password_token(
    token: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> ResetPasswordTokenResponse | RedirectResponse:
    logger.info("Password reset token validation attempt")
    try:
        validate_password_reset_token(db, token)
    except TokenExpiredError:
        logger.warning("Expired password reset token used")
        return _expired_redirect()
    except InvalidTokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResetPasswordTokenResponse(valid=True, message="Token is valid.")


@router.post(
    "/reset-password",
    summary="Reset password with token",
    description=(
        "Reset a user's password using a valid reset token. "
        "Returns an expiration message if the token has expired."
    ),
    responses={
        200: {"description": "Password reset successful"},
        410: {
            "description": "Token expired",
            "model": ExpiredTokenResponse,
        },
        400: {"description": "Invalid reset link"},
    },
)
async def reset_user_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    logger.info("Password reset attempt")
    try:
        reset_password(db, request.token, request.new_password)
    except TokenExpiredError as exc:
        logger.warning("Expired password reset token used during password reset")
        raise HTTPException(
            status_code=410,
            detail={
                "message": str(exc),
                "redirect_url": PASSWORD_RESET_REQUEST_PATH,
            },
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info("Password reset successful")
    return {"message": "Password has been reset successfully."}
