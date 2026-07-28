from fastapi import APIRouter

from src.endpoints import user_authentication

router = APIRouter(prefix="/api/v1")
router.include_router(user_authentication.router)
