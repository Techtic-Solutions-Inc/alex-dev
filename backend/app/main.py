"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.schemas.common import SuccessResponse
from app.schemas.health import HealthData, HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    application.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(application)

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Check service health",
    )
    async def root_health() -> SuccessResponse[HealthData]:
        return SuccessResponse(
            message="Service is operational.",
            data=HealthData(status="UP"),
        )

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
