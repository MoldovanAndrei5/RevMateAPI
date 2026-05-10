from typing import List

from fastapi import APIRouter, Depends

from schemas.task_schema import TaskSuggestionRequest, TaskSuggestionResponse
from services.ai_service import AIService
from utils.auth import get_current_user

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

def get_ai_service() -> AIService:
    return AIService()

@router.post("/suggestions")
def get_task_suggestions(body: TaskSuggestionRequest, service: AIService = Depends(get_ai_service)):
    return service.get_task_suggestions(request_data=body.model_dump())