import os
import httpx
from fastapi import APIRouter, Depends, HTTPException

from schemas.task_schema import TaskSuggestionRequest
from utils.auth import get_current_user

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")

import logging
logger = logging.getLogger()

@router.post("/suggestions")
def get_task_suggestions(body: TaskSuggestionRequest):
    try:
        logger.info(f"Calling AI service at: {AI_SERVICE_URL}/ai/suggestions")
        response = httpx.post(
            f"{AI_SERVICE_URL}/ai/suggestions",
            json=body.model_dump(mode="json"),
            timeout=25,
        )
        logger.info(f"AI service status: {response.status_code}")
        logger.info(f"AI service response: {response.text}")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI service unavailable")
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=500, detail="AI service timed out")
    except httpx.ConnectError as e:
        raise HTTPException(status_code=500, detail=f"Cannot connect to AI service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {e}")