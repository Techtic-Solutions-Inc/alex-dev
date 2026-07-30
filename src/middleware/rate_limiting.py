import ipaddress
from collections.abc import Awaitable, Callable
from enum import Enum
from inspect import isawaitable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate, RateItem
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


# Loopback and private networks commonly used by reverse proxies (e.g. nginx, ALB).
_DEFAULT_TRUSTED_PROXY_NETWORKS: tuple[
    ipaddress.IPv4Network | ipaddress.IPv6Network, ...
] = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)

_trusted_proxy_networks: tuple[
    ipaddress.IPv4Network | ipaddress.IPv6Network, ...
] = _DEFAULT_TRUSTED_PROXY_NETWORKS


def _parse_ip_network(value: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    value = value.strip()
    if not value:
        return None
    try:
        if "/" in value:
            return ipaddress.ip_network(value, strict=False)
        address = ipaddress.ip_address(value)
        return ipaddress.ip_network(f"{address}/{address.max_prefixlen}", strict=False)
    except ValueError:
        return None


def _parse_ip_address(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def configure_trusted_proxies(proxies: list[str] | None = None) -> None:
    """Configure CIDRs/IPs whose requests may include a trusted X-Forwarded-For chain."""
    global _trusted_proxy_networks
    if not proxies:
        _trusted_proxy_networks = _DEFAULT_TRUSTED_PROXY_NETWORKS
        return

    networks = tuple(network for proxy in proxies if (network := _parse_ip_network(proxy)) is not None)
    _trusted_proxy_networks = networks if networks else _DEFAULT_TRUSTED_PROXY_NETWORKS


def _is_trusted_proxy(ip: str) -> bool:
    address = _parse_ip_address(ip)
    if address is None:
        return False
    return any(address in network for network in _trusted_proxy_networks)


def get_client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else "127.0.0.1"
    peer_address = _parse_ip_address(peer_ip)
    fallback = str(peer_address) if peer_address else "127.0.0.1"

    # Ignore X-Forwarded-For unless the direct peer is a trusted reverse proxy.
    if not _is_trusted_proxy(fallback):
        return fallback

    forwarded = request.headers.get("X-Forwarded-For")
    if not forwarded:
        return fallback

    chain = [part.strip() for part in forwarded.split(",") if part.strip()]

    # Strip trusted proxy hops from the right; the rightmost remaining IP is the client.
    while chain and _is_trusted_proxy(chain[-1]):
        chain.pop()

    if chain:
        client_address = _parse_ip_address(chain[-1])
        if client_address is not None:
            return str(client_address)

    return fallback


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


def create_rate_limiter(requests: int, window_seconds: int, strategy: RateLimitStrategy) -> Callable:
    limiter = create_limiter(requests, window_seconds)
    identifier_func = IDENTIFIER_MAP[strategy]

    async def rate_limiter_dependency(request: Request, response: Response) -> None:
        identifier = await identifier_func(request)
        try:
            limiter.try_acquire(identifier)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            ) from e

    return rate_limiter_dependency


def setup_rate_limiting(app: FastAPI, settings: Settings) -> None:
    if not settings.rate_limit_enabled:
        return

    configure_trusted_proxies(settings.rate_limit_trusted_proxies)

    limiter = create_limiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
    identifier_func = IDENTIFIER_MAP[RateLimitStrategy(settings.rate_limit_strategy)]

    class RateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
            if request.url.path in settings.rate_limit_excluded_paths:
                return await call_next(request)

            identifier = await identifier_func(request)
            try:
                limiter.try_acquire(identifier)
            except Exception as e:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                )

            return await call_next(request)

    app.add_middleware(RateLimitMiddleware)
