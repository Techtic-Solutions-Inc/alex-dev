"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.api.routes import api_router
from src.config.logging import logger
from src.config.migrations import run_migrations
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
    run_migrations()
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

    app.include_router(api_router)

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
                "description": "Invalid or expired authentication token.",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "message": "Invalid or expired token.",
                            "error": {"code": "UNAUTHORIZED", "details": None},
                        }
                    }
                },
            },
            403: {
                "description": "Missing JWT token.",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "message": (
                                "Authentication is required to access this resource."
                            ),
                            "error": {"code": "FORBIDDEN", "details": None},
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
