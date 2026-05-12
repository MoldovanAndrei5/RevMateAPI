from abc import ABC, abstractmethod
from uuid import UUID
from schemas.car_schema import CarSchema, CarCreate, CarUpdate
from schemas.response_schema import MessageResponse

class ICarService(ABC):
    @abstractmethod
    def get_user_cars(self, user_id: int) -> list[CarSchema]: ...
    
    @abstractmethod
    def get_car(self, car_uuid: UUID, user_id: int) -> CarSchema: ...
    
    @abstractmethod
    def create_car(self, data: CarCreate, user_id: int) -> CarSchema: ...
    
    @abstractmethod
    def update_car(self, car_uuid: UUID, user_id: int, data: CarUpdate) -> CarSchema: ...
    
    @abstractmethod
    def delete_car(self, car_uuid: UUID, user_id: int) -> MessageResponse: ...
    
    @abstractmethod
    def generate_report(self, car_uuid: UUID, user_id: int) -> tuple[bytes, str]: ...
