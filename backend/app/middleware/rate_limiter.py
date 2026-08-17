"""Simple process-local rate limiter for API requests."""

from __future__ import annotations

import time
from collections import deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit client IPs within a rolling time window.

    Deployments with multiple workers should replace this store with Redis or
    another shared backend so limits remain global.
    """

    def __init__(self, app, requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self._requests = requests
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in {"/docs", "/openapi.json", "/redoc"}:
            return await call_next(request)
        client_key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        history = self._hits.setdefault(client_key, deque())
        cutoff = now - self._window_seconds
        while history and history[0] <= cutoff:
            history.popleft()
        if len(history) >= self._requests:
            retry_after = max(1, int(self._window_seconds - (now - history[0])))
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Too many requests. Please try again shortly.",
                    "error": {"code": "RATE_LIMITED", "details": None},
                },
                headers={"Retry-After": str(retry_after)},
            )
        history.append(now)
        return await call_next(request)
