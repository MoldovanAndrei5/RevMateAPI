import boto3
import os
from botocore.exceptions import ClientError

ses_client = boto3.client('ses', region_name=os.getenv('AWS_REGION'))
SENDER = os.getenv('SES_SENDER_EMAIL')

def send_otp_email(to_email: str, otp_code: str) -> bool:
    try:
        ses_client.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "RevMate — Verify your email"},
                "Body": {
                    "Html": {
                        "Data": f"""
                            <h2>Welcome to RevMate!</h2>
                            <p>Your verification code is:</p>
                            <h1 style="letter-spacing: 8px">{otp_code}</h1>
                            <p>This code expires in 10 minutes.</p>
                        """
                    }
                }
            }
        )
        return True
    except ClientError:
        return False