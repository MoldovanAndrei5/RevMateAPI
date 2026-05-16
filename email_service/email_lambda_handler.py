import json
import os
import boto3
from botocore.exceptions import ClientError

SENDER = os.getenv('SES_SENDER_EMAIL')
_ses_client = None

def _get_ses_client():
    global _ses_client
    if _ses_client is None:
        _ses_client = boto3.client('ses', region_name=os.getenv('SES_REGION'))
    return _ses_client

def _send_otp_email(to_email: str, otp_code: str) -> bool:
    try:
        _get_ses_client().send_email(
            Source=SENDER,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "RevMate — Verify your email"},
                "Body": {
                    "Html": {
                        "Data": f"""
                            <h2>Welcome to RevMate!</h2>
                            <p>Your verification code is:</p>
                            <h1 style="letter-spacing: 8px; font-family: monospace;">{otp_code}</h1>
                            <p>This code expires in 10 minutes.</p>
                            <p>If you did not request this, please ignore this email.</p>
                        """
                    }
                }
            }
        )
        return True
    except ClientError as e:
        print(f"Failed to send email: {e}")
        return False

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
            return _response(400, {"detail": "email and otp_code are required"})

        success = _send_otp_email(to_email, otp_code)
        if not success:
            return _response(500, {"detail": "Failed to send email"})

        return _response(200, {"message": "Email sent successfully"})

    except Exception as e:
        print(f"Unexpected error: {e}")
        return _response(500, {"detail": f"Unexpected error: {str(e)}"})