import os
from fastapi import HTTPException
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse
from services.interfaces.i_upload_service import IUploadService
from utils.s3 import generate_presigned_upload_url

ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/pdf"
}

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
ALLOWED_FOLDERS = {"invoices", "cars"}

class UploadService(IUploadService):        
    def get_presigned_url(self, body: PresignedUrlRequest) -> PresignedUrlResponse:
        if body.file_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"File type {body.file_type} not allowed")
        if body.file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        if body.folder not in ALLOWED_FOLDERS:
            raise HTTPException(status_code=400, detail="Invalid folder")
        result = generate_presigned_upload_url(
            folder=body.folder,
            file_name=body.file_name,
            content_type=body.file_type
        )
        return PresignedUrlResponse(
            upload_url=result["upload_url"],
            file_key=result["file_key"]
        )
