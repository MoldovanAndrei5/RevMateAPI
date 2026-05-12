from fastapi import APIRouter, Depends
from dependencies.di import get_upload_service
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse
from services.interfaces.i_upload_service import IUploadService
from utils.auth import get_current_user

router = APIRouter(tags=["Upload"], dependencies=[Depends(get_current_user)])

@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(body: PresignedUrlRequest, upload_service: IUploadService = Depends(get_upload_service)):
    return upload_service.get_presigned_url(body)