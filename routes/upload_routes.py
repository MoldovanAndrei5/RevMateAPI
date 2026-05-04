from fastapi import APIRouter, Depends, HTTPException
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse
from utils.s3 import generate_presigned_upload_url
from utils.auth import get_current_user

router = APIRouter(tags=["Upload"], dependencies=[Depends(get_current_user)])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "application/pdf"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(
    body: PresignedUrlRequest,
    user_id: int = Depends(get_current_user)
):
    if body.file_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {body.file_type} not allowed")

    if body.file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    if body.folder not in ("invoices", "cars"):
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