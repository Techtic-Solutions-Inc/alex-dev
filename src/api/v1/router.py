from fastapi import APIRouter

from src.api.v1.routes.auth_routes import router as auth_router
from src.api.v1.routes.health_routes import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["authentication"])
