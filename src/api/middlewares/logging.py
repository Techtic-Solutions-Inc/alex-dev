import time

from fastapi import Request
from loguru import logger


async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info("Request: {} {}", request.method, request.url.path)

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    logger.info(
        "Response: {} {} ({}s)",
        request.method,
        response.status_code,
        f"{duration:.3f}",
    )
    return response
