"""Authentication token endpoints."""

from fastapi import APIRouter, status

from app.core.config import get_settings
from app.core.security import InvalidTokenError, create_access_token, decode_token
from app.exceptions.http_exceptions import AppHTTPException
from app.schemas.auth import RefreshTokenRequest, RefreshTokenResponse, TokenData
from app.schemas.common import ErrorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh an access token",
    description=(
        "Exchanges a valid, unexpired refresh JWT for a new access JWT. The request body is "
        "explicitly typed so its `refresh_token` field is available in Swagger UI."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Malformed request."},
        401: {"model": ErrorResponse, "description": "Refresh token is invalid or expired."},
        403: {"model": ErrorResponse, "description": "Refresh token is not permitted."},
        404: {"model": ErrorResponse, "description": "Authentication resource was not found."},
        409: {"model": ErrorResponse, "description": "Token refresh conflicts with its state."},
        422: {"model": ErrorResponse, "description": "Request validation failed."},
        500: {"model": ErrorResponse, "description": "Unexpected server error."},
    },
)
async def refresh_access_token(body: RefreshTokenRequest) -> RefreshTokenResponse:
    """Validate a refresh token and return a new access token."""
    try:
        payload = decode_token(body.refresh_token, "refresh")
    except InvalidTokenError as exc:
        raise AppHTTPException(
            401,
            "INVALID_REFRESH_TOKEN",
            "The refresh token is invalid or expired.",
        ) from exc

    settings = get_settings()
    return RefreshTokenResponse(
        message="Access token refreshed.",
        data=TokenData(
            access_token=create_access_token(str(payload["sub"])),
            expires_in=settings.jwt_expiry,
        ),
    )
