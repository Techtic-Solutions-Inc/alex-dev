"""Global exception handlers producing the API's standard error envelope."""

from collections import defaultdict
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.exceptions.http_exceptions import AppHTTPException

logger = get_logger(__name__)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    """Create a safe, consistent JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error": {"code": code, "details": details},
        },
    )


def _validation_details(exc: RequestValidationError) -> dict[str, list[str]]:
    fields: defaultdict[str, list[str]] = defaultdict(list)
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        fields[location or "request"].append(error["msg"])
    return dict(fields)


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized handlers for expected and unexpected API failures."""

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        _: Request, exc: AppHTTPException
    ) -> JSONResponse:
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            422,
            "VALIDATION_ERROR",
            "One or more fields are invalid.",
            _validation_details(exc),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if exc.status_code == 404:
            return error_response(404, "RESOURCE_NOT_FOUND", "The requested resource was not found.")
        if exc.status_code == 405:
            return error_response(405, "METHOD_NOT_ALLOWED", "The request method is not allowed.")
        return error_response(exc.status_code, "REQUEST_ERROR", "The request could not be processed.")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled request error path=%s", request.url.path, exc_info=exc)
        return error_response(500, "INTERNAL_SERVER_ERROR", "An unexpected error occurred.")
