import json
from email_service import EmailService
from logger import get_logger


service = EmailService()
logger = get_logger(__name__)

def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def handler(event, context):
    try:
        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)

        to_email = body.get("email")
        otp_code = body.get("otp_code")

        if not to_email or not otp_code:
            logger.warning("Missing email or otp code in request")
            return _response(400, {"detail": "email and otp_code are required"})

        success = service.send_otp_email(to_email, otp_code)
        if not success:
            return _response(500, {"detail": "Failed to send email"})

        return _response(200, {"message": "Email sent successfully"})

    except Exception as e:
        logger.error(f"Unexpected error in email handler: {e}")
        return _response(500, {"detail": f"Unexpected error: {str(e)}"})