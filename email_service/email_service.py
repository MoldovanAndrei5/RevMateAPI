import os
import boto3
from botocore.exceptions import ClientError

class EmailService:
    SENDER = os.getenv('SES_SENDER_EMAIL')
    
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name=os.getenv('SES_REGION'))

    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        try:
            self.ses_client.send_email(
                Source=self.SENDER,
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