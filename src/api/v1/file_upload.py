@router.post(
    '/upload', 
    response_model=FileUploadResponse, 
    responses={
        400: {'description': 'Invalid file type or file too large.'},
        401: {'description': 'Unauthorized.'},
        403: {'description': 'Forbidden.'}
    }
)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the storage service.

    - **file**: The file to upload (must be JPEG or PNG and less than 5MB).
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    if file.size > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=400, detail="File too large.")
    file_url = await file_storage_service.store_file(file)
    return JSONResponse(content={"url": file_url})