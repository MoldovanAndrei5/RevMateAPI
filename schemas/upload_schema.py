from pydantic import BaseModel

class PresignedUrlRequest(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    folder: str  # "invoices" or "cars"


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str