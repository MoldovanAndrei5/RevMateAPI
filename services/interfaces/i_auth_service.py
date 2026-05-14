from abc import ABC, abstractmethod
from schemas.auth_schema import AuthResponse
from schemas.response_schema import MessageResponse
from schemas.user_schema import UserLogin, UserCreate, UserUpdate

class IAuthService(ABC):
    @abstractmethod
    def login(self, data: UserLogin) -> AuthResponse: ...

    @abstractmethod
    def send_otp(self, email: str) -> MessageResponse: ...
    
    @abstractmethod
    def register(self, data: UserCreate) -> MessageResponse: ...
    
    @abstractmethod
    def reset_password(self, user_id: int, data: UserUpdate) -> MessageResponse: ...
