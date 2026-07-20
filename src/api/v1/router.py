from fastapi import APIRouter

from src.api.v1.reset_password import router as reset_password_router

router = APIRouter()
router.include_router(reset_password_router, tags=["auth"])
