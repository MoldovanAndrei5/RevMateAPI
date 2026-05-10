import os
import httpx
from fastapi import APIRouter, Depends, HTTPException

from schemas.task_schema import TaskSuggestionRequest
from utils.auth import get_current_user

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")

@router.post("/suggestions")
def get_task_suggestions(body: TaskSuggestionRequest):
    response = httpx.post(
        f"{AI_SERVICE_URL}/suggestions",
        json=body.model_dump(mode="json"),
        timeout=25,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI service unavailable")
    return response.json()