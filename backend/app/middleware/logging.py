import time

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Request: {method} {url} - Response: {status} ({duration:.2f}ms)",
            method=request.method,
            url=request.url,
            status=response.status_code,
            duration=duration_ms,
        )
        return response
