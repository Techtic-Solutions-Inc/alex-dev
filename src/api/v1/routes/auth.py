from fastapi import APIRouter
from src.api.v1.controllers.auth import router as auth_controller

router = APIRouter()

router.include_router(auth_controller, prefix='/auth', tags=['auth'])
