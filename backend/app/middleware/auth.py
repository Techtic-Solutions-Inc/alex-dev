from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_token
from app.exceptions.http_exceptions import ForbiddenException, UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

_VALID_USER_ROLES = frozenset({"user", "admin"})


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


async def require_user_role(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Require an authenticated user with user or admin role."""
    role = current_user.get("role", "user")
    if role not in _VALID_USER_ROLES:
        raise ForbiddenException(
            message="Access denied",
            code="FORBIDDEN",
        )
    return current_user


async def require_admin_role(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Require an authenticated user with admin role."""
    role = current_user.get("role", "user")
    if role != "admin":
        raise ForbiddenException(
            message="Admin access required",
            code="FORBIDDEN",
        )
    return current_user
