from abc import ABC, abstractmethod
from schemas.user_schema import UserLogin, UserCreate


class IAuthService(ABC):
    @abstractmethod
    def login(self, data: UserLogin) -> dict: ...

    @abstractmethod
    def send_otp(self, email: str) -> dict: ...
    
    @abstractmethod
    def register(self, data: UserCreate) -> dict: ...
