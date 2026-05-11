import json
import os

import boto3
import httpx
from fastapi import APIRouter, Depends, HTTPException

from schemas.task_schema import TaskSuggestionRequest
from utils.auth import get_current_user

router = APIRouter(tags=["AI"], dependencies=[Depends(get_current_user)])

lambda_client = boto3.client('lambda', region_name=os.getenv("AWS_REGION"))

@router.post("/suggestions")
def get_task_suggestions(body: TaskSuggestionRequest):
    try:
        response = lambda_client.invoke(
            FunctionName='aiService',
            InvocationType='RequestResponse',
            Payload=json.dumps(body.model_dump(mode="json")).encode('utf-8')
        )

        result = json.loads(response['Payload'].read())

        if result.get('statusCode') != 200:
            detail = json.loads(result.get('body', '{}')).get('detail', 'AI service unavailable')
            raise HTTPException(status_code=500, detail=detail)

        return json.loads(result['body'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")