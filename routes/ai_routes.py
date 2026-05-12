from fastapi import APIRouter, Depends
from dependencies.di import get_ai_proxy_service
from schemas.task_schema import TaskSuggestionRequest, TaskSuggestionResponse
from services.interfaces.i_ai_proxy_service import IAIProxyService
from utils.auth import get_current_user

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

@router.post("/suggestions", response_model=list[TaskSuggestionResponse])
def get_task_suggestions(body: TaskSuggestionRequest, ai_proxy_service: IAIProxyService = Depends(get_ai_proxy_service)):
    return ai_proxy_service.get_suggestions(body)
