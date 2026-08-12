from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_token
from app.exceptions.http_exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """Extract and validate the current user from a JWT access token."""
    if not token:
        raise UnauthorizedException(
            message="Authentication required",
            code="UNAUTHORIZED",
        )
    try:
        payload = verify_token(token)
    except ValueError:
        raise UnauthorizedException(
            message="Invalid or expired token",
            code="INVALID_TOKEN",
        )
    if "sub" not in payload:
        raise UnauthorizedException(
            message="Invalid token payload",
            code="INVALID_TOKEN",
        )
    return payload
