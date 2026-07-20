import logging
from collections.abc import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

MUTATING_METHODS = {"POST", "PUT", "PATCH"}
JSON_CONTENT_TYPE = "application/json"


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate request headers for mutating JSON endpoints."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in MUTATING_METHODS:
            content_type = request.headers.get("content-type", "")
            if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
                return await call_next(request)

            if content_type and not content_type.startswith(JSON_CONTENT_TYPE):
                logger.warning(
                    "Rejected request with unsupported content type: %s %s",
                    request.method,
                    content_type,
                )
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": {
                            "message": "Content-Type must be application/json",
                            "code": "unsupported_media_type",
                        }
                    },
                )

        return await call_next(request)
