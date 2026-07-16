from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.middlewares.rate_limiting import (
    RateLimitCriteria,
    RateLimiter,
    rate_limiting_middleware,
    reset_rate_limiter,
)


class FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, int] = {}
        self._expiry: dict[str, int] = {}

    def incr(self, key: str) -> int:
        self._store[key] = self._store.get(key, 0) + 1
        return self._store[key]

    def expire(self, key: str, seconds: int) -> bool:
        self._expiry[key] = seconds
        return True

    def ttl(self, key: str) -> int:
        return self._expiry.get(key, -1)

    def delete(self, key: str) -> int:
        existed = int(key in self._store)
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return existed


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def rate_limiter(fake_redis: FakeRedis) -> RateLimiter:
    return RateLimiter(
        redis_client=fake_redis,
        max_requests=2,
        window_seconds=60,
    )


@pytest.fixture(autouse=True)
def clear_rate_limiter_cache() -> None:
    reset_rate_limiter()
    yield
    reset_rate_limiter()


def test_rate_limit_exceeded(rate_limiter: RateLimiter) -> None:
    first = rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")
    second = rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")
    third = rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")

    assert first.allowed is True
    assert first.current_count == 1
    assert second.allowed is True
    assert second.current_count == 2
    assert third.allowed is False
    assert third.current_count == 3


def test_rate_limit_reset(rate_limiter: RateLimiter) -> None:
    rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")
    rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")

    blocked = rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")
    assert blocked.allowed is False

    rate_limiter.reset(RateLimitCriteria.IP, "127.0.0.1")

    allowed = rate_limiter.check_and_increment(RateLimitCriteria.IP, "127.0.0.1")
    assert allowed.allowed is True
    assert allowed.current_count == 1


def test_rate_limit_by_user_uses_authorization_header(rate_limiter: RateLimiter) -> None:
    user_one = rate_limiter.check_and_increment(RateLimitCriteria.USER, "token-user-1")
    user_two = rate_limiter.check_and_increment(RateLimitCriteria.USER, "token-user-2")

    assert user_one.allowed is True
    assert user_two.allowed is True
    assert user_one.current_count == 1
    assert user_two.current_count == 1


@pytest.mark.anyio
async def test_rate_limiting_middleware_returns_429(rate_limiter: RateLimiter) -> None:
    request = MagicMock(spec=Request)
    request.headers = {}
    request.client = MagicMock(host="203.0.113.10")

    call_next = AsyncMock(
        return_value=JSONResponse(content={"ok": True}, status_code=200),
    )

    rate_limiter.check_and_increment(RateLimitCriteria.IP, "203.0.113.10")
    rate_limiter.check_and_increment(RateLimitCriteria.IP, "203.0.113.10")

    response = await rate_limiting_middleware(
        request,
        call_next,
        rate_limiter=rate_limiter,
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    call_next.assert_not_awaited()


@pytest.mark.anyio
async def test_rate_limiting_middleware_adds_headers_when_allowed(
    rate_limiter: RateLimiter,
) -> None:
    request = MagicMock(spec=Request)
    request.headers = {}
    request.client = MagicMock(host="203.0.113.11")

    downstream_response = JSONResponse(content={"ok": True}, status_code=200)
    call_next = AsyncMock(return_value=downstream_response)

    response = await rate_limiting_middleware(
        request,
        call_next,
        rate_limiter=rate_limiter,
    )

    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "2"
    assert response.headers["X-RateLimit-Remaining"] == "1"
    call_next.assert_awaited_once()


def test_rate_limiting_middleware_integration() -> None:
    fake_redis = FakeRedis()
    limiter = RateLimiter(
        redis_client=fake_redis,
        max_requests=1,
        window_seconds=60,
    )

    app = FastAPI()

    @app.middleware("http")
    async def test_rate_limit_middleware(request: Request, call_next):
        return await rate_limiting_middleware(
            request,
            call_next,
            rate_limiter=limiter,
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)

    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200
    assert first.headers["X-RateLimit-Remaining"] == "0"
    assert second.status_code == 429
    assert second.json()["detail"] == "Rate limit exceeded. Please try again later."
