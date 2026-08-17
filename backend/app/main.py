"""FastAPI application entry point and infrastructure registration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import engine
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Release database resources cleanly when the API process exits."""
    configure_logging()
    yield
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure the API application."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "REST API foundation with versioned routes, JWT authentication, standardized error "
            "responses, request validation, and operational health checks."
        ),
        version="1.0.0",
        openapi_tags=[
            {"name": "Health", "description": "Public availability and readiness endpoints."},
            {"name": "Authentication", "description": "JWT token lifecycle endpoints."},
        ],
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    # The unversioned route supports infrastructure tooling; its v1 alias supports API clients.
    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()
