from fastapi import FastAPI

from src.database import init_db
from src.routers.auth import router as auth_router

app = FastAPI(title="User Authentication System")

app.include_router(auth_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
