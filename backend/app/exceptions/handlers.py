from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Handle validation errors
    if request.url.path.rstrip('/').endswith('/auth/login'):
        # Specific handling for login endpoint
        pass
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
