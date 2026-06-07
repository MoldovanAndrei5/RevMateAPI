from abc import ABC, abstractmethod
from schemas.user_schema import UserLogin, UserCreate, UserResetPassword


class IAuthService(ABC):
    @abstractmethod
    def login(self, data: UserLogin) -> dict: ...

    @abstractmethod
    def send_register_otp(self, email: str) -> dict: ...
    
    @abstractmethod
    def register(self, data: UserCreate) -> dict: ...
    
    @abstractmethod
    def send_forgot_password_otp(self, email: str) -> dict: ...
    
    @abstractmethod
    def reset_forgotten_password(self, data: UserResetPassword) -> dict: ...
