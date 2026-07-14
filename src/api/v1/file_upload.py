from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.file_storage_service import FileStorageService
from schemas.file_schema import FileUploadRequest, FileUploadResponse

router = APIRouter()
file_storage_service = FileStorageService()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the storage service.

    - **file**: The file to upload.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    if file.size > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=400, detail="File too large.")
    file_url = await file_storage_service.store_file(file)
    return JSONResponse(content={"url": file_url})