from abc import ABC, abstractmethod
from schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse

class IUploadService(ABC):
    @abstractmethod
    def get_presigned_url(self, body: PresignedUrlRequest) -> dict: ...
