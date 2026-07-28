from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.router import api_router
from src.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="alex-dev", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)
