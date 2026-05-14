from abc import ABC, abstractmethod
from models.otp_code import OtpCode

class IOtpRepository(ABC):
    @abstractmethod
    def create_or_replace(self, otp: OtpCode) -> OtpCode: ...

    @abstractmethod
    def get_by_email(self, email: str) -> OtpCode | None: ...

    @abstractmethod
    def delete(self, otp: OtpCode) -> None: ...