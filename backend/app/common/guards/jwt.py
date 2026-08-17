"""Reusable bearer-token guard for protected FastAPI routes."""

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.exceptions.http_exceptions import APIException

_bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Bearer access token returned by an authentication endpoint.",
)


def require_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> dict[str, Any]:
    """Validate and return access-token claims for route dependencies."""
    if credentials is None:
        raise APIException("Authentication is required.", 401, "AUTHENTICATION_REQUIRED")
    try:
        return decode_token(credentials.credentials, "access")
    except ValueError as exc:
        raise APIException("Access token is invalid or expired.", 401, "INVALID_ACCESS_TOKEN") from exc
