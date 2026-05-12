from abc import ABC, abstractmethod
from uuid import UUID
from models import Car

class ICarRepository(ABC):
    @abstractmethod
    def get_all_by_user(self, user_id: int) -> list[Car]: ...
    
    @abstractmethod
    def get_by_uuid(self, car_uuid: UUID) -> Car | None: ...
    
    @abstractmethod
    def create(self, car: Car) -> Car: ...
    
    @abstractmethod
    def update(self, car_uuid: UUID, data: dict) -> Car | None: ...
    
    @abstractmethod
    def delete(self, car: Car) -> None: ...
           