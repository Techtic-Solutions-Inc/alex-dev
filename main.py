"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.api.routes.auth import router as auth_router
from src.api.routes.health import router as health_router
from src.api.routes.signup import router as signup_router
from src.config.logging import logger
from src.config.settings import get_settings
from src.exceptions.handlers import register_exception_handlers
from src.middlewares.auth import get_current_user
from src.middlewares.logging import log_requests

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting FastAPI application in {} mode", settings.environment)
    yield
    logger.info("Shutting down FastAPI application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="FastAPI Backend",
        description=(
            "Backend API built with FastAPI and PostgreSQL. Provides authentication, "
            "structured error handling, logging, and OpenAPI documentation."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    def rate_limit_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )

    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(log_requests)

    register_exception_handlers(app)

    app.include_router(health_router, tags=["Health"])
    app.include_router(auth_router, tags=["Authentication"])
    app.include_router(signup_router, tags=["Authentication"])

    @app.get(
        "/protected-endpoint",
        summary="Protected endpoint for JWT middleware verification",
        description=(
            "Returns the authenticated user identifier extracted from the JWT. "
            "Requires a valid Bearer token in the Authorization header."
        ),
        responses={
            200: {
                "description": "Authenticated user identifier.",
                "content": {
                    "application/json": {
                        "example": {"user": "550e8400-e29b-41d4-a716-446655440000"},
                    }
                },
            },
            401: {
                "description": "Missing or invalid authentication token.",
                "content": {
                    "application/json": {
                        "examples": {
                            "not_authenticated": {
                                "summary": "No token provided",
                                "value": {"detail": "Not authenticated"},
                            },
                            "invalid_token": {
                                "summary": "Invalid token",
                                "value": {"detail": "Invalid authentication credentials"},
                            },
                        }
                    }
                },
            },
        },
        tags=["Authentication"],
    )
    async def protected_endpoint(
        current_user: str = Depends(get_current_user),
    ) -> dict:
        return {"user": current_user}

    return app


app = create_app()
