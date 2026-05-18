from abc import ABC, abstractmethod
from models.user import User

class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def create(self, user: User) -> User: ...
    
    @abstractmethod
    def update_password(self, user_id: int, hashed_password: str) -> User | None: ...
    
    @abstractmethod
    def delete(self, user_id: int) -> None: ...
