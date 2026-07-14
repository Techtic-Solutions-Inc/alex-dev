from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    """
    Schema for file upload request.
    """
    file: str

class FileUploadResponse(BaseModel):
    """
    Schema for file upload response.
    """
    url: str