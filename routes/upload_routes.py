from fastapi import APIRouter, Depends
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse
from services.upload_service import UploadService
from utils.auth import get_current_user

router = APIRouter(tags=["Upload"], dependencies=[Depends(get_current_user)])

def get_upload_service() -> UploadService:
    return UploadService()

@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(body: PresignedUrlRequest, service: UploadService = Depends(get_upload_service)):
    return service.get_presigned_url(body)