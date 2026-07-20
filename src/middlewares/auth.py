import logging
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from src.config.settings import settings
from src.db.session import get_db
from src.models.user import User
from src.utils.security import decode_access_token

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def _is_public_path(path: str) -> bool:
    normalized = path.rstrip("/") or "/"
    if normalized.startswith("/public"):
        return True
    for public_path in settings.PUBLIC_PATHS:
        public_normalized = public_path.rstrip("/") or "/"
        if normalized == public_normalized:
            return True
    return False


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT tokens and attach authenticated user context to requests."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        if request.method == "OPTIONS" or _is_public_path(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "message": "Missing or invalid authorization header",
                        "code": "authentication_error",
                    }
                },
            )

        token = authorization.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
        except jwt.PyJWTError as exc:
            logger.warning("JWT validation failed: %s", exc)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "message": "Invalid or expired token",
                        "code": "authentication_error",
                    }
                },
            )

        request.state.user_id = payload.get("sub")
        request.state.user_email = payload.get("email")
        return await call_next(request)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    token: str | None = None
    if credentials is not None:
        token = credentials.credentials
    elif hasattr(request.state, "user_id"):
        user_id = request.state.user_id
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        logger.warning("JWT decode failed in dependency: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
