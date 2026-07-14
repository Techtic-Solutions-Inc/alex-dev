from fastapi import APIRouter
from .file_upload import router as file_upload_router

router = APIRouter()
router.include_router(file_upload_router, prefix="/files", tags=["files"])
from fastapi import FastAPI
from src.api.v1.routes.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix='/api/v1')
