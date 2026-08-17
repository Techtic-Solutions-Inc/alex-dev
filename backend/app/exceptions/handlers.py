"""Global exception handlers enforcing the public API response contract."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.http_exceptions import APIException

logger = logging.getLogger(__name__)


def _error(message: str, code: str, details: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": {"code": code, "details": details},
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Attach response-safe exception handlers to an application."""

    @app.exception_handler(APIException)
    async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error(exc.message, exc.code, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details: dict[str, list[str]] = {}
        for error in exc.errors():
            location = error.get("loc", ())
            field = ".".join(str(part) for part in location if part != "body")
            details.setdefault(field or "request", []).append(error["msg"])
        validation_status = (
            status.HTTP_400_BAD_REQUEST
            if request.url.path.rstrip("/").endswith("/auth/login")
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return JSONResponse(
            status_code=validation_status,
            content=_error("Validation failed.", "VALIDATION_ERROR", details),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error for %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error("An unexpected error occurred.", "INTERNAL_SERVER_ERROR"),
        )
