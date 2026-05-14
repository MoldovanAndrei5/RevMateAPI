from sqlalchemy import Column, String, DateTime
from database import Base

class OtpCode(Base):
    __tablename__ = "otp_codes"

    email = Column(String, primary_key=True)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)