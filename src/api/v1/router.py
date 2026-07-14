from fastapi import APIRouter
from .file_upload import router as file_upload_router

router = APIRouter()
router.include_router(file_upload_router, prefix="/files", tags=["files"])