from fastapi import APIRouter

from api.routes.auth import router as auth_router
from api.routes.profile import router as profile_router
from api.routes.user_routes import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(profile_router, prefix="/api/profile", tags=["profile"])
api_router.include_router(user_router, prefix="/api/users", tags=["users"])
