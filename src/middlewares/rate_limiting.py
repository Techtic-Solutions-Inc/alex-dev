import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Protocol

import redis
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from src.config.settings import (
    RATE_LIMIT_CRITERIA,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
    REDIS_SOCKET_TIMEOUT,
    REDIS_URL,
)

logger = logging.getLogger(__name__)


class RateLimitCriteria(str, Enum):
    IP = "ip"
    USER = "user"


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    current_count: int
    limit: int
    reset_after: int


class RedisClientProtocol(Protocol):
    def incr(self, key: str) -> int: ...

    def expire(self, key: str, seconds: int) -> bool: ...

    def ttl(self, key: str) -> int: ...

    def delete(self, key: str) -> int: ...


class RateLimiter:
    """Tracks request counts in Redis and enforces fixed-window rate limits."""

    KEY_PREFIX = "rate_limit"

    def __init__(
        self,
        redis_client: RedisClientProtocol,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than zero")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        self._redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _build_key(self, criteria: RateLimitCriteria, identifier: str) -> str:
        return f"{self.KEY_PREFIX}:{criteria.value}:{identifier}"

    def check_and_increment(
        self,
        criteria: RateLimitCriteria,
        identifier: str,
    ) -> RateLimitResult:
        key = self._build_key(criteria, identifier)
        current_count = self._redis.incr(key)

        if current_count == 1:
            self._redis.expire(key, self.window_seconds)

        ttl = self._redis.ttl(key)
        reset_after = ttl if ttl > 0 else self.window_seconds

        return RateLimitResult(
            allowed=current_count <= self.max_requests,
            current_count=current_count,
            limit=self.max_requests,
            reset_after=reset_after,
        )

    def reset(self, criteria: RateLimitCriteria, identifier: str) -> None:
        key = self._build_key(criteria, identifier)
        self._redis.delete(key)


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _get_user_identifier(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()
    return token or None


def _resolve_identifier(
    request: Request,
    criteria: RateLimitCriteria,
) -> str:
    if criteria == RateLimitCriteria.USER:
        user_identifier = _get_user_identifier(request)
        if user_identifier:
            return user_identifier

    return _get_client_ip(request)


def _create_redis_client() -> Optional[redis.Redis]:
    if not RATE_LIMIT_ENABLED:
        return None

    try:
        client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=REDIS_SOCKET_TIMEOUT,
        )
        client.ping()
        return client
    except redis.RedisError as exc:
        logger.warning("Rate limiting disabled: unable to connect to Redis: %s", exc)
        return None


_redis_client: Optional[redis.Redis] = None
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> Optional[RateLimiter]:
    global _redis_client, _rate_limiter

    if not RATE_LIMIT_ENABLED:
        return None

    if _rate_limiter is None:
        _redis_client = _create_redis_client()
        if _redis_client is None:
            return None

        _rate_limiter = RateLimiter(
            redis_client=_redis_client,
            max_requests=RATE_LIMIT_MAX_REQUESTS,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS,
        )

    return _rate_limiter


def reset_rate_limiter() -> None:
    """Reset cached Redis client and limiter instances (primarily for tests)."""
    global _redis_client, _rate_limiter

    if _redis_client is not None:
        try:
            _redis_client.close()
        except redis.RedisError:
            logger.exception("Failed to close Redis client")

    _redis_client = None
    _rate_limiter = None


def _build_rate_limit_response(result: RateLimitResult) -> JSONResponse:
    remaining = max(result.limit - result.current_count, 0)
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "limit": result.limit,
            "remaining": remaining,
            "reset_after": result.reset_after,
        },
        headers={
            "Retry-After": str(result.reset_after),
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(result.reset_after),
        },
    )


def _apply_rate_limit_headers(response: Response, result: RateLimitResult) -> None:
    remaining = max(result.limit - result.current_count, 0)
    response.headers["X-RateLimit-Limit"] = str(result.limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(result.reset_after)


async def rate_limiting_middleware(
    request: Request,
    call_next: Callable,
    rate_limiter: Optional[RateLimiter] = None,
) -> Response:
    limiter = rate_limiter if rate_limiter is not None else get_rate_limiter()
    if limiter is None:
        return await call_next(request)

    criteria = RateLimitCriteria(RATE_LIMIT_CRITERIA)
    identifier = _resolve_identifier(request, criteria)

    try:
        result = limiter.check_and_increment(criteria, identifier)
    except redis.RedisError as exc:
        logger.error("Rate limiting check failed: %s", exc)
        return await call_next(request)

    if not result.allowed:
        logger.warning(
            "Rate limit exceeded for %s=%s (%s/%s requests)",
            criteria.value,
            identifier,
            result.current_count,
            result.limit,
        )
        return _build_rate_limit_response(result)

    response = await call_next(request)
    _apply_rate_limit_headers(response, result)
    return response
