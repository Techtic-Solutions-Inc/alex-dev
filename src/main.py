from fastapi import FastAPI

from src.api.v1.router import router as v1_router
from src.database import init_db

app = FastAPI(title="User Authentication System")

app.include_router(v1_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
