import ipaddress
from collections.abc import Awaitable, Callable
from enum import Enum
from inspect import isawaitable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pyrate_limiter import Duration, Limiter, RequestRate
from pyrate_limiter.exceptions import BucketFullException
from starlette.responses import Response

from src.config import Settings

RATE_LIMIT_EXCEEDED_DETAIL = "Rate limit exceeded"


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
    return get_client_ip(request)


async def user_identifier(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if authorization:
        return authorization
    return get_client_ip(request)


async def ip_and_path_identifier(request: Request) -> str:
    return f"{get_client_ip(request)}:{request.url.path}"


IDENTIFIER_MAP: dict[
    RateLimitStrategy,
    Callable[[Request], str | Awaitable[str]],
] = {
    RateLimitStrategy.IP: ip_identifier,
    RateLimitStrategy.USER: user_identifier,
    RateLimitStrategy.IP_AND_PATH: ip_and_path_identifier,
}


async def _resolve_identifier(
    request: Request,
    identifier_func: Callable[[Request], str | Awaitable[str]],
) -> str:
    result = identifier_func(request)
    if isawaitable(result):
        return await result
    return result


def create_limiter(requests: int, window_seconds: int) -> Limiter:
    return Limiter(RequestRate(requests, Duration.SECOND * window_seconds))


def reset_rate_limiters() -> None:
    Limiter.bucket_group.clear()


def create_rate_limiter(
    requests: int,
    window_seconds: int,
    strategy: RateLimitStrategy,
) -> Callable[[Request], Awaitable[None]]:
    limiter = create_limiter(requests, window_seconds)
    identifier_func = IDENTIFIER_MAP[strategy]

    async def rate_limit_dependency(request: Request) -> None:
        identifier = await _resolve_identifier(request, identifier_func)
        try:
            limiter.try_acquire(f"route:{identifier}")
        except BucketFullException as exc:
            raise HTTPException(
                status_code=429,
                detail=RATE_LIMIT_EXCEEDED_DETAIL,
            ) from exc

    return rate_limit_dependency


def setup_rate_limiting(app: FastAPI, settings: Settings) -> None:
    if not settings.rate_limit_enabled:
        return

    configure_trusted_proxies(settings.rate_limit_trusted_proxies)

    limiter = create_limiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
    identifier_func = IDENTIFIER_MAP[RateLimitStrategy(settings.rate_limit_strategy)]
    excluded_paths = set(settings.rate_limit_excluded_paths)

    @app.middleware("http")
    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in excluded_paths:
            return await call_next(request)

        identifier = await _resolve_identifier(request, identifier_func)
        try:
            limiter.try_acquire(f"global:{identifier}")
        except BucketFullException:
            return JSONResponse(
                status_code=429,
                content={"detail": RATE_LIMIT_EXCEEDED_DETAIL},
            )

        return await call_next(request)
