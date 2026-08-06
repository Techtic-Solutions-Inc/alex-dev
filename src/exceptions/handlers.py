"""Exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.exceptions.http_exceptions import AppHTTPException
from src.schemas.responses import (
    ErrorResponse,
    ValidationErrorItem,
    ValidationErrorResponse,
)


def _build_error_response(
    *,
    message: str,
    code: str,
    details=None,
) -> dict:
    """Build a consistent error response payload."""
    return ErrorResponse(
        success=False,
        message=message,
        error={"code": code, "details": details},
    ).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """Register global and custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_response(
                message=exc.message,
                code=exc.code,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            location = error.get("loc", ())
            field = ".".join(str(part) for part in location if part != "body")
            errors.append(
                ValidationErrorItem(
                    field=field or "body",
                    message=error.get("msg", "Invalid value"),
                )
            )

        validation_response = ValidationErrorResponse(errors=errors)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                **_build_error_response(
                    message="Validation Error",
                    code="VALIDATION_ERROR",
                    details=validation_response.errors,
                ),
                "detail": validation_response.detail,
                "errors": [item.model_dump() for item in validation_response.errors],
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception for {} {}",
            request.method,
            request.url,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal Server Error",
                **_build_error_response(
                    message="Internal Server Error",
                    code="INTERNAL_SERVER_ERROR",
                    details=None,
                ),
            },
        )
