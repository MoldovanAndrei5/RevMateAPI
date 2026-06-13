import os
from fastapi import HTTPException
from schemas.upload_schema import PresignedUrlRequest
from services.interfaces.i_upload_service import IUploadService
from utils.s3 import generate_presigned_upload_url
from utils.logger import get_logger


logger = get_logger(__name__)
ALLOWED_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/pdf"
}
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
ALLOWED_FOLDERS = {"invoices", "cars"}

class UploadService(IUploadService):        
    def get_presigned_url(self, body: PresignedUrlRequest) -> dict:
        logger.info(f"Generating presigned url for {body.file_name} in {body.folder}")
        if body.file_type not in ALLOWED_TYPES:
            logger.warning(f"Unsupported file type: {body.file_type}")
            raise HTTPException(status_code=400, detail=f"File type {body.file_type} not allowed")
        if body.file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {body.file_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes")
            raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE} bytes limit")
        if body.folder not in ALLOWED_FOLDERS:
            logger.warning(f"Unsupported folder: {body.folder}")
            raise HTTPException(status_code=400, detail="Invalid folder")
        result = generate_presigned_upload_url(
            folder=body.folder,
            file_name=body.file_name,
            content_type=body.file_type
        )
        logger.info("Presigned url generated successfully")
        return {
            "upload_url": result["upload_url"],
            "file_key": result["file_key"]
        }
