"""FastAPI application factory and production middleware registration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, health
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.mongo import create_mongo_client
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database client lifecycle without failing liveness at startup."""
    client = create_mongo_client()
    app.state.mongo_client = client
    app.state.database = client[settings.DB_NAME]
    try:
        yield
    finally:
        client.close()


def create_application() -> FastAPI:
    """Create the configured application for ASGI servers and tests."""
    configure_logging()
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "REST API with MongoDB persistence and JWT authentication. "
            "All responses use a stable success/error envelope."
        ),
        version=settings.APP_VERSION,
        openapi_tags=[
            {"name": "Health", "description": "Service liveness and readiness probes."},
            {"name": "Authentication", "description": "Account and session management."},
        ],
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.RATE_LIMIT_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    # The Real Estate Professional frontend contract uses unversioned auth paths.
    # Retain the versioned routes above for existing clients during this transition.
    app.include_router(auth.router, prefix="/api")
    return app


app = create_application()
