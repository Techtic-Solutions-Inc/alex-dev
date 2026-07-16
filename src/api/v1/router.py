from fastapi import APIRouter

from src.api.v1.admin_login import router as admin_login_router
from src.api.v1.login import router as login_router
from src.api.v1.register import router as register_router
from src.api.v1.reset_password import router as reset_password_router

router = APIRouter()
router.include_router(login_router, tags=["auth"])
router.include_router(register_router, tags=["auth"])
router.include_router(admin_login_router, tags=["admin-auth"])
router.include_router(reset_password_router, tags=["auth"])
