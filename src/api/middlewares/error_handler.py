from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

from api.exceptions import HTTPError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(HTTPError)
    async def http_error_handler(request: Request, exc: HTTPError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
