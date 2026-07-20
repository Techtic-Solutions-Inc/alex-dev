import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.v1.router import api_router
from src.config.settings import settings
from src.db.session import engine
from src.middlewares.setup import create_limiter, register_middleware
from src.models.base import Base
from src.utils.error_handlers import register_exception_handlers
from src.utils.logging_config import configure_logging
from src.views.home import render_welcome_page

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application in %s environment", settings.ENVIRONMENT)
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend API with authentication, PostgreSQL, and JWT security.",
        version="1.0.0",
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    limiter = create_limiter()
    register_middleware(app, limiter)
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    app.mount("/public", StaticFiles(directory="public"), name="public")

    @app.get("/", include_in_schema=False)
    def root():
        return render_welcome_page(settings.APP_NAME)

    return app


app = create_app()
