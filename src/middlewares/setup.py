from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.config.settings import settings
from src.middlewares.auth import JWTAuthMiddleware
from src.middlewares.logging import RequestLoggingMiddleware
from src.middlewares.request_validation import RequestValidationMiddleware


def create_limiter() -> Limiter:
    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT] if settings.RATE_LIMIT_ENABLED else [],
        enabled=settings.RATE_LIMIT_ENABLED and not settings.is_testing,
    )


def register_middleware(app: FastAPI, limiter: Limiter) -> None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
