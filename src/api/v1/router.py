from fastapi import APIRouter

from src.api.v1.authenticate import router as authenticate_router

router = APIRouter()
router.include_router(authenticate_router)
