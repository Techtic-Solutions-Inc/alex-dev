from fastapi import APIRouter
from src.api.v1.endpoints import login, register

api_router = APIRouter()
api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(register.router, prefix="/auth", tags=["auth"])