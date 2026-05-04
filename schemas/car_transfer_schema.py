from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class CarTransferInitiate(BaseModel):
    car_uuid: UUID
    receiver_email: EmailStr

class CarTransferOutgoingResponse(BaseModel):
    transfer_uuid: UUID
    receiver_email: str
    receiver_first_name: str
    receiver_last_name: str
    status: str
    created_at: datetime
    expires_at: datetime
    car_name: str
    car_make: str
    car_model: str
    car_year: int

    class Config:
        from_attributes = True
        
class CarTransferIncomingResponse(BaseModel):
    transfer_uuid: UUID
    sender_email: EmailStr
    sender_first_name: str
    sender_last_name: str
    status: str
    created_at: datetime
    expires_at: datetime
    car_name: str
    car_make: str
    car_model: str
    car_year: int
    
    class Config:
        from_attributes = True
        