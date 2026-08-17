"""Authorization dependencies for protected endpoints."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import InvalidTokenError, decode_token
from app.exceptions.http_exceptions import AppHTTPException

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="JWT bearer authentication",
    description="Provide an access token as `Bearer <token>`.",
)


async def get_current_subject(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """Return the authenticated subject or raise a safe 401 response."""
    if credentials is None:
        raise AppHTTPException(401, "AUTHENTICATION_REQUIRED", "Authentication is required.")
    try:
        payload = decode_token(credentials.credentials, "access")
    except InvalidTokenError as exc:
        raise AppHTTPException(401, "INVALID_ACCESS_TOKEN", "The access token is invalid or expired.") from exc
    return str(payload["sub"])
