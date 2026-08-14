from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import create_access_token, create_refresh_token, verify_token
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.auth import assert_valid_user_role, oauth2_scheme
from app.schemas.auth import RefreshTokenRequest, RefreshTokenResponse, TokenData

router = APIRouter()
protected_router = APIRouter()


async def _require_valid_token(
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """Validate that a bearer token is present and cryptographically valid."""
    if not token:
        raise UnauthorizedException(
            message="Authentication required",
            code="UNAUTHORIZED",
        )
    try:
        payload = verify_token(token, expected_type=None)
    except ValueError:
        raise UnauthorizedException(
            message="Invalid or expired token",
            code="INVALID_TOKEN",
        )
    assert_valid_user_role(payload)
    return payload


@protected_router.get("/protected-endpoint")
async def read_protected(
    _user: dict[str, Any] = Depends(_require_valid_token),
) -> dict[str, str]:
    return {"message": "This is a protected endpoint"}


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(body: RefreshTokenRequest) -> RefreshTokenResponse:
    """Exchange a valid refresh token for a new access/refresh token pair."""
    try:
        payload = verify_token(body.refresh_token, expected_type="refresh")
    except ValueError:
        raise UnauthorizedException(
            message="Invalid or expired token",
            code="INVALID_TOKEN",
        )

    assert_valid_user_role(payload)

    token_data = {
        "sub": payload["sub"],
        "role": payload.get("role", "user"),
    }
    return RefreshTokenResponse(
        success=True,
        message="Token refreshed successfully",
        data=TokenData(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        ),
    )
