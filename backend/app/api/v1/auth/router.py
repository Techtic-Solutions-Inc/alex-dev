from fastapi import APIRouter

from app.api.v1.auth.password_recovery import router as password_recovery_router
from app.api.v1.auth.signin import router as signin_router
from app.api.v1.auth.signup import router as signup_router

auth_router = APIRouter()
auth_router.include_router(signup_router)
auth_router.include_router(signin_router)
auth_router.include_router(password_recovery_router)
