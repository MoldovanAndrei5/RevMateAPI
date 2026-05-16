import json
import os
import httpx
from fastapi import HTTPException
from schemas.task_schema import TaskSuggestionRequest, TaskSuggestionResponse
from services.interfaces.i_ai_proxy_service import IAIProxyService

PRIVATE_SERVICE_URL = os.getenv("PRIVATE_SERVICE_URL")

class AIProxyService(IAIProxyService):
    def get_suggestions(self, body: TaskSuggestionRequest) -> list[TaskSuggestionResponse]:
        try:
            response = httpx.post(
                f"{PRIVATE_SERVICE_URL}/ai/suggestions",
                json=body.model_dump(mode="json"),
                timeout=25,
            )
            result = response.json()
            inner_status = result.get("statusCode", 200)
            inner_body = result.get("body", "[]")

            if isinstance(inner_body, str):
                inner_body = json.loads(inner_body)

            if inner_status != 200:
                detail = inner_body.get("detail", "AI service error") if isinstance(inner_body, dict) else "AI service error"
                raise HTTPException(status_code=inner_status, detail=detail)

            return inner_body

        except HTTPException:
            raise
        except httpx.TimeoutException:
            raise HTTPException(status_code=500, detail="AI service timed out")
        except httpx.ConnectError as e:
            raise HTTPException(status_code=500, detail=f"Cannot connect to AI service: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI service error: {e}")