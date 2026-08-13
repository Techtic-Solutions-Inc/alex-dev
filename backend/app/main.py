from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.about.router import router as about_router
from app.api.v1.auth.router import auth_router
from app.api.v1.blog.router import router as blog_router
from app.api.v1.content.router import router as content_router
from app.api.v1.content_library.router import router as content_library_router
from app.api.v1.endpoints import health
from app.api.v1.profile.router import router as profile_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    yield


app = FastAPI(
    title="Backend API",
    description="Production-ready FastAPI backend with JWT authentication",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(auth_router, prefix="/api/auth")
app.include_router(blog_router, prefix="/api/blog", tags=["Blog"])
app.include_router(content_router, prefix="/api/content", tags=["Content"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(about_router, prefix="/api/about", tags=["About"])
app.include_router(
    content_library_router,
    prefix="/api/content-library",
    tags=["Content Library"],
)
app.include_router(api_router, prefix="/api/v1")
