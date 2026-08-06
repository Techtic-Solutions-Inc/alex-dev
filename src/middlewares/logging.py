"""Request/response logging middleware."""

from fastapi import Request
from loguru import logger


async def log_requests(request: Request, call_next):
    """Log incoming requests and outgoing responses."""
    response = await call_next(request)
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Response: {response.status_code}"
    )
    return response
