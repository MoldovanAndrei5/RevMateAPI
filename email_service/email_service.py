import os
import boto3
from botocore.exceptions import ClientError
from logger import get_logger


logger = get_logger(__name__)

class EmailService:
    SENDER = os.getenv('SES_SENDER_EMAIL')
    
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name=os.getenv('SES_REGION'))

    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        logger.info(f"Sending OTP email to {to_email}")
        try:
            self.ses_client.send_email(
                Source=self.SENDER,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": "RevMate email verification code"},
                    "Body": {
                        "Html": {
                            "Data": f"""
                                <p>Your verification code is:</p>
                                <h1 style="letter-spacing: 8px; font-family: monospace;">{otp_code}</h1>
                                <p>This code expires in 10 minutes.</p>
                                <p>If you did not request this, please contact support.</p>
                            """
                        }
                    }
                }
            )
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
        except ClientError as e:
            logger.error(f"Failed to send OTP email to {to_email}: {e}")
            return False