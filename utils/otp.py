import secrets
from datetime import datetime, timezone, timedelta
from models.otp_code import OtpCode

OTP_EXPIRE_MINUTES = 10

def generate_otp(email: str) -> OtpCode:
    otp_code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    return OtpCode(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
