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
    