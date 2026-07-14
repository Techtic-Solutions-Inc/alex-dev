from fastapi import FastAPI
from src.api.v1.routes.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix='/api/v1')
