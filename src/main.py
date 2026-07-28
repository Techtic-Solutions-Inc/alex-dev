from fastapi import FastAPI

from src.api.v1.router import router as v1_router
from src.config import get_settings
from src.database import Base, engine
from src.models import User  # noqa: F401

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(v1_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
