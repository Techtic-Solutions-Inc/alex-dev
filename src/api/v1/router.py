from fastapi import APIRouter

from src.api.v1 import authenticate

router = APIRouter()
router.include_router(authenticate.router)
