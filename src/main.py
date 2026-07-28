from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import get_settings
from src.database import Base, engine
from src.endpoints.router import router
from src.logging_config import configure_logging
from src.models import User  # noqa: F401

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
