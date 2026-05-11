import boto3
import json
import os
from fastapi import APIRouter, Depends, HTTPException
from schemas.task_schema import TaskSuggestionRequest, TaskSuggestionResponse
from utils.auth import get_current_user

class AILambdaClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = boto3.client('lambda', region_name=os.getenv("AI_LAMBDA_REGION"))
        return cls._client

    @classmethod
    def invoke(cls, function_name: str, payload: dict) -> dict:
        response = cls.get_client().invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload).encode('utf-8')
        )
        return json.loads(response['Payload'].read())

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

@router.post("/suggestions", response_model=list[TaskSuggestionResponse])
def get_task_suggestions(body: TaskSuggestionRequest):
    try:
        result = AILambdaClient.invoke(
            function_name='aiService',
            payload=body.model_dump(mode="json")
        )
        
        if result.get('statusCode') != 200:
            detail = json.loads(result.get('body', '{}')).get('detail', 'AI service unavailable')
            raise HTTPException(status_code=500, detail=detail)

        return json.loads(result['body'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")