"""Process-local fixed-window rate limiting middleware."""

from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit each client IP to a configurable number of requests per time window."""

    def __init__(self, app: ASGIApp, requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self._request_times: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_key = request.client.host if request.client else "unknown"
        now = monotonic()
        timestamps = self._request_times[client_key]
        while timestamps and timestamps[0] <= now - self.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= self.requests:
            retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "success": False,
                    "message": "Too many requests. Please try again shortly.",
                    "error": {"code": "RATE_LIMIT_EXCEEDED", "details": None},
                },
            )

        timestamps.append(now)
        return await call_next(request)
