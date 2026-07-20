"""FastAPI application entry point."""

import logging

from fastapi import FastAPI

from src.api.v1.routes import api_router
from src.config.database import Base, engine
from src.config.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables on application startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
