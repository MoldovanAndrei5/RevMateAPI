from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from typing import Optional

class TaskSchema(BaseModel):
    task_uuid: UUID
    car_uuid: UUID
    title: str
    category: str
    mileage: Optional[int] = None
    cost: Optional[Decimal] = None
    scheduled_date: Optional[int] = None
    completed_date: Optional[int] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class TaskCreate(BaseModel):
    task_uuid: UUID
    car_uuid: UUID
    title: str
    category: str
    mileage: Optional[int] = None
    cost: Optional[Decimal] = None
    scheduled_date: Optional[int] = None
    completed_date: Optional[int] = None
    notes: Optional[str] = None
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    mileage: Optional[int] = None
    cost: Optional[Decimal] = None
    scheduled_date: Optional[int] = None
    completed_date: Optional[int] = None
    notes: Optional[str] = None
    
class TaskSuggestionRequest(BaseModel):
    car_uuid: UUID
    make: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    transmission_type: str
    last_oil_change_km: Optional[int] = None
    known_issues: Optional[str] = None
    
class TaskSuggestionResponse(BaseModel):
    car_uuid: UUID
    title: str
    category: str
    mileage: Optional[int] = None
    scheduled_date: Optional[int] =None
    notes: Optional[str] = None