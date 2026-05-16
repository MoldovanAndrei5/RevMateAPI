from abc import ABC, abstractmethod

class IEmailProxyService(ABC):
    @abstractmethod
    def send_otp(self, email: str, otp_code: str) -> None: ...
