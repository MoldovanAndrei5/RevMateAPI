import json
from ai_service import AIService
from logger import get_logger


service = AIService()
logger = get_logger(__name__)

def _response(status_code: int, body: dict | list) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def handler(event, context):
    try:
        if "body" in event:
            body = event["body"]
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event
        suggestions = service.get_task_suggestions(request_data=body)
        logger.info(f"Returning {len(suggestions)} suggestions")
        return _response(200, [s.model_dump(mode="json") for s in suggestions])
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return _response(400, {"detail": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error in AI handler: {e}")
        return _response(500, {"detail": f"Unexpected error: {str(e)}"})