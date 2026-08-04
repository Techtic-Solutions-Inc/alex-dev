import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import config.logging  # noqa: F401
from api.middlewares.error_handler import register_error_handlers
from api.router import api_router
from api.middlewares.logging import logging_middleware
from api.middlewares.rate_limiter import limiter, rate_limit_exceeded_handler
from config.migrations import (
    check_database_connectivity,
    get_current_revision,
    get_head_revision,
    has_pending_migrations,
    run_migrations,
)

load_dotenv()


def should_auto_migrate() -> bool:
    auto_migrate = os.getenv("AUTO_MIGRATE", "true").lower()
    return auto_migrate not in {"0", "false", "no", "off"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if should_auto_migrate():
        try:
            await asyncio.to_thread(run_migrations)
        except Exception as exc:
            logger.error(f"Database migration failed: {exc}")
            raise
    yield


app = FastAPI(
    title="Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(api_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await logging_middleware(request, call_next)


@app.get("/health")
def health_check():
    """Verify the API is running and healthy."""
    return {"status": "healthy"}


@app.get("/health/db")
async def db_health_check():
    """Check database connectivity and migration status."""
    db_reachable = await asyncio.to_thread(check_database_connectivity)
    if not db_reachable:
        return {
            "status": "unhealthy",
            "database": "unreachable",
            "current_revision": None,
            "head_revision": None,
            "pending_migrations": None,
        }

    try:
        current = await asyncio.to_thread(get_current_revision)
        head = await asyncio.to_thread(get_head_revision)
        pending = await asyncio.to_thread(has_pending_migrations)
    except Exception as exc:
        logger.warning("Migration status check failed: {}", exc)
        return {
            "status": "degraded",
            "database": "reachable",
            "current_revision": None,
            "head_revision": None,
            "pending_migrations": None,
            "error": str(exc),
        }

    return {
        "status": "healthy" if not pending else "pending_migrations",
        "database": "reachable",
        "current_revision": current,
        "head_revision": head,
        "pending_migrations": pending,
    }
