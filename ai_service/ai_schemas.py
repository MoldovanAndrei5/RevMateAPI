from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TaskSuggestionResponse(BaseModel):
    car_uuid: UUID
    title: str
    category: str
    mileage: Optional[int] = None
    scheduled_date: Optional[int] = None
    notes: Optional[str] = None