import json
from ai_service import AIService

def handler(event, context):
    try:
        if "body" in event:
            body = event["body"]
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event

        service = AIService()
        suggestions = service.get_task_suggestions(request_data=body)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps([s.model_dump(mode="json") for s in suggestions])
        }
    except ValueError as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": f"Unexpected error: {str(e)}"})
        }