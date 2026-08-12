from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.http_exceptions import AppHTTPException


def _error_response(
    message: str,
    code: str,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": {
            "code": code,
            "details": details,
        },
    }


def register_exception_handlers(app: Any) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(exc.message, exc.code, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        field_errors = []
        for error in exc.errors():
            loc = error.get("loc", ())
            field = ".".join(str(part) for part in loc if part != "body")
            field_errors.append(
                {
                    "field": field or "body",
                    "message": error.get("msg", "Invalid value"),
                }
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_response(
                message="Validation error",
                code="VALIDATION_ERROR",
                details=field_errors,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code_map = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(
                message=str(exc.detail),
                code=code_map.get(exc.status_code, "HTTP_ERROR"),
                details=None,
            ),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled exception: {}", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_response(
                message="An unexpected error occurred",
                code="INTERNAL_SERVER_ERROR",
                details=None,
            ),
        )
