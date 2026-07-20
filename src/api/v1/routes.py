from fastapi import APIRouter
from src.api.v1.controllers.register_controller import router as register_router

router = APIRouter()

router.include_router(register_router, prefix="/api/v1")