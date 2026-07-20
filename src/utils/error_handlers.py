import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.utils.exceptions import AppException

logger = logging.getLogger(__name__)


def _build_error_payload(
    *,
    message: str,
    error_code: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "message": message,
            "code": error_code,
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    logger.warning("Application error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
        ),
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_payload(
            message="Internal server error",
            error_code="internal_error",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
