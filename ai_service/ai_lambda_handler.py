import json
from ai_service import AIService

service = AIService()

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
        return _response(200, [s.model_dump(mode="json") for s in suggestions])
    except ValueError as e:
        return _response(400, {"detail": str(e)})
    except Exception as e:
        return _response(500, {"detail": f"Unexpected error: {str(e)}"})