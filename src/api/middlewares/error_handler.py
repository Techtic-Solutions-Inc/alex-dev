from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from api.exceptions import HTTPError


def _error_message(detail: object) -> str:
    if isinstance(detail, str):
        return detail
    return str(detail)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        message = _error_message(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error": message},
        )

    @app.exception_handler(HTTPError)
    async def http_error_handler(request: Request, exc: HTTPError):
        message = _error_message(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error": message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        detail = exc.errors()
        message = "Validation error"
        if detail:
            first = detail[0]
            loc = first.get("loc", ())
            field = loc[-1] if loc else "request"
            message = f"Invalid value for {field}"
        return JSONResponse(
            status_code=422,
            content={"detail": detail, "error": message},
        )
