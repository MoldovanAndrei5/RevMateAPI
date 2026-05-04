from uuid import UUID

from pydantic import BaseModel
from typing import Optional

class CarSchema(BaseModel):
    car_uuid: UUID
    user_id: int
    name: str
    make: str
    model: str
    year: int
    vin: str
    mileage: int
    license_plate: str
    image_key: Optional[str] = None

    class Config:
        from_attributes = True
        
class CarCreate(BaseModel):
    car_uuid: UUID
    name: str
    make: str
    model: str
    year: int
    vin: str
    mileage: int
    license_plate: str
    image_key: Optional[str] = None
    
class CarUpdate(BaseModel):
    name: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None
    license_plate: Optional[str] = None
    image_key: Optional[str] = None