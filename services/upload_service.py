from fastapi import HTTPException
from repositories.upload_repository import UploadRepository
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/pdf"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_FOLDERS = {"invoices", "cars"}

class UploadService:
    def __init__(self):
        self.repo = UploadRepository()
        
    def get_presigned_url(self, body: PresignedUrlRequest) -> PresignedUrlResponse:
        if body.file_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"File type {body.file_type} not allowed")
        if body.file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        if body.folder not in ALLOWED_FOLDERS:
            raise HTTPException(status_code=400, detail="Invalid folder")
        result = self.repo.generate_presigned_url(
            folder=body.folder,
            file_name=body.file_name,
            content_type=body.file_type
        )
        return PresignedUrlResponse(
            upload_url=result["upload_url"],
            file_key=result["file_key"]
        )