from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.endpoints import health
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import close_database_client, db, ping_database
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    try:
        await db.client.start_session()
        await ping_database()
        logger.info("MongoDB connection established")
    except Exception as exc:
        logger.error("MongoDB connection failed: {}", exc)
        raise
    yield
    await close_database_client()
    logger.info("MongoDB connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-ready FastAPI backend with MongoDB, JWT authentication, "
        "structured logging, and rate limiting."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Additional request/response logging hook as specified in project setup."""
    logger.info("Request: {method} {url}", method=request.method, url=request.url)
    response = await call_next(request)
    logger.info("Response: {status}", status=response.status_code)
    return response
