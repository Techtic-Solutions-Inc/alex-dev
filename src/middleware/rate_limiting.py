from collections.abc import Awaitable, Callable
from enum import Enum
from inspect import isawaitable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, InMemoryBucket, Limiter, Rate, RateItem
from pyrate_limiter.abstracts import AbstractBucket, BucketFactory
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config import Settings, get_settings

IdentifierFunc = Callable[[Request], Awaitable[str]]
SkipFunc = Callable[[Request], Awaitable[bool]]
MiddlewareCallback = Callable[[Request], Awaitable[JSONResponse]]
DependencyCallback = Callable[[Request, Response], None]


class RateLimitStrategy(str, Enum):
    IP = "ip"
    USER = "user"
    IP_AND_PATH = "ip_and_path"


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


async def ip_identifier(request: Request) -> str:
    return f"ip:{get_client_ip(request)}"


async def user_identifier(request: Request) -> str:
    user_id = request.headers.get("X-User-Id")
    if user_id:
        return f"user:{user_id.strip()}"

    authorization = request.headers.get("Authorization")
    if authorization:
        return f"user:{authorization.strip()}"

    return f"ip:{get_client_ip(request)}"


async def ip_and_path_identifier(request: Request) -> str:
    return f"{get_client_ip(request)}:{request.scope['path']}"


IDENTIFIER_MAP: dict[RateLimitStrategy, IdentifierFunc] = {
    RateLimitStrategy.IP: ip_identifier,
    RateLimitStrategy.USER: user_identifier,
    RateLimitStrategy.IP_AND_PATH: ip_and_path_identifier,
}


class KeyedBucketFactory(BucketFactory):
    """Route each rate-limit key to its own in-memory bucket."""

    def __init__(self, rates: list[Rate]) -> None:
        self.rates = rates
        self._buckets: dict[str, AbstractBucket] = {}

    def wrap_item(self, name: str, weight: int = 1) -> RateItem | Awaitable[RateItem]:
        bucket = self._get_or_create_bucket(name)
        now = bucket.now()

        if isawaitable(now):

            async def wrap_async() -> RateItem:
                return RateItem(name, await now, weight=weight)

            return wrap_async()

        return RateItem(name, now, weight=weight)

    def get(self, item: RateItem) -> AbstractBucket:
        return self._get_or_create_bucket(item.name)

    def _get_or_create_bucket(self, name: str) -> AbstractBucket:
        if name not in self._buckets:
            self._buckets[name] = self.create(InMemoryBucket, self.rates)
        return self._buckets[name]


def create_limiter(requests: int, window_seconds: int) -> Limiter:
    rates = [Rate(requests, Duration.SECOND * window_seconds)]
    return Limiter(KeyedBucketFactory(rates))


def get_identifier(strategy: RateLimitStrategy | str) -> IdentifierFunc:
    if isinstance(strategy, str):
        strategy = RateLimitStrategy(strategy)
    return IDENTIFIER_MAP[strategy]


def build_rate_limit_headers(settings: Settings) -> dict[str, str]:
    return {
        "Retry-After": str(settings.rate_limit_window_seconds),
        "X-RateLimit-Limit": str(settings.rate_limit_requests),
    }


def create_rate_limit_exceeded_callback(
    settings: Settings,
) -> MiddlewareCallback:
    headers = build_rate_limit_headers(settings)

    async def rate_limit_exceeded_callback(_request: Request) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."},
            headers=headers,
        )

    return rate_limit_exceeded_callback


def create_dependency_rate_limit_callback() -> DependencyCallback:
    def rate_limit_exceeded_callback(_request: Request, _response: Response) -> None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    return rate_limit_exceeded_callback


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limiter: Limiter,
        identifier: IdentifierFunc,
        callback: MiddlewareCallback,
        skip: SkipFunc | None = None,
        blocking: bool = False,
    ) -> None:
        super().__init__(app)
        self.limiter = limiter
        self.identifier = identifier
        self.callback = callback
        self.skip = skip
        self.blocking = blocking

    async def dispatch(self, request: Request, call_next):
        if self.skip and await self.skip(request):
            return await call_next(request)

        rate_key = await self.identifier(request)
        success = await self.limiter.try_acquire_async(rate_key, blocking=self.blocking)
        if not success:
            return await self.callback(request)

        return await call_next(request)


def create_skip_rate_limit(excluded_paths: set[str]) -> SkipFunc:
    async def skip_rate_limit(request: Request) -> bool:
        return request.url.path in excluded_paths

    return skip_rate_limit


def setup_rate_limiting(app: FastAPI, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.rate_limit_enabled:
        return

    excluded_paths = set(settings.rate_limit_excluded_paths)
    limiter = create_limiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)

    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        identifier=get_identifier(settings.rate_limit_strategy),
        callback=create_rate_limit_exceeded_callback(settings),
        skip=create_skip_rate_limit(excluded_paths),
    )


def create_rate_limiter(
    requests: int | None = None,
    window_seconds: int | None = None,
    strategy: RateLimitStrategy | str | None = None,
) -> RateLimiter:
    settings = get_settings()
    resolved_requests = requests if requests is not None else settings.rate_limit_requests
    resolved_window = (
        window_seconds if window_seconds is not None else settings.rate_limit_window_seconds
    )
    resolved_strategy = strategy if strategy is not None else settings.rate_limit_strategy

    return RateLimiter(
        limiter=create_limiter(resolved_requests, resolved_window),
        identifier=get_identifier(resolved_strategy),
        callback=create_dependency_rate_limit_callback(),
    )
