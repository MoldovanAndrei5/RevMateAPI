import json
import os
import httpx
from fastapi import HTTPException
from services.interfaces.i_email_proxy_service import IEmailProxyService
from utils.logger import get_logger


logger = get_logger(__name__)
PRIVATE_SERVICE_URL = os.getenv("PRIVATE_SERVICE_URL")

class EmailProxyService(IEmailProxyService):
    def send_otp(self, email: str, otp_code: str) -> None:
        logger.info(f"Sending OTP to {email}")
        try:
            response = httpx.post(
                f"{PRIVATE_SERVICE_URL}/email/send-otp",
                json={"email": email, "otp_code": otp_code},
                timeout=25,
            )
            result = response.json()
            inner_status = result.get("statusCode", 200)
            inner_body = result.get("body", "{}")
            
            if isinstance(inner_body, str):
                inner_body = json.loads(inner_body)
            if inner_status != 200:
                detail = inner_body.get("detail", "Email service error") if isinstance(inner_body, dict) else "Email service error"
                raise HTTPException(status_code=500, detail=detail)
            logger.info(f"OTP sent successfully to {email}")
        except HTTPException:
            raise
        except httpx.TimeoutException:
            logger.error(f"Email service timed out for {email}")
            raise HTTPException(status_code=500, detail="Email service timed out")
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to email service: {e}")
            raise HTTPException(status_code=500, detail=f"Cannot connect to email service: {e}")
        except Exception as e:
            logger.error(f"Email service error for {email}: {e}")
            raise HTTPException(status_code=500, detail=f"Email service error: {e}")