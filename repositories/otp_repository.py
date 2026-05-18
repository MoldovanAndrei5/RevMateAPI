from sqlalchemy.orm import Session
from models.otp_code import OtpCode
from repositories.interfaces.i_otp_repository import IOtpRepository


class OtpRepository(IOtpRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_replace(self, otp: OtpCode) -> OtpCode:
        existing = self.get_by_email(otp.email)
        if existing:
            self.delete(existing)
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp
        
    def get_by_email(self, email: str) -> OtpCode | None:
        return self.db.query(OtpCode).filter(OtpCode.email == email).first()
    
    def delete(self, otp: OtpCode) -> None:
        self.db.delete(otp)
        self.db.commit()