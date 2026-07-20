from fastapi import FastAPI
from src.api.v1.router import api_router
from src.config.settings import settings

app = FastAPI()

# Include routers
app.include_router(api_router)

# Middleware and other app configurations can be added here