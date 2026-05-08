from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class InvoiceCreate(BaseModel):
    task_uuid: UUID
    file_key: str
    file_name: str
    file_type: str
    file_size: int


class InvoiceResponse(BaseModel):
    invoice_uuid: UUID
    task_uuid: UUID
    file_key: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
    
class InvoiceDownloadResponse(BaseModel):
    download_url: str