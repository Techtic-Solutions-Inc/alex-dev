"""API route definitions."""

from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.health import router as health_router
from src.api.routes.signup import router as signup_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(signup_router, tags=["Authentication"])
