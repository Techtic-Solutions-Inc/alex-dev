from fastapi import APIRouter

from src.api.v1.user_authenticate import router as user_authenticate_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_authenticate_router)
