from abc import ABC, abstractmethod
from uuid import UUID
from models import Car
from models.car_transfer import CarTransfer
from models.user import User

class ITransferRepository(ABC):
    @abstractmethod
    def get_pending_by_car(self, car_uuid: UUID) -> CarTransfer | None: ...
    
    @abstractmethod
    def get_pending_by_uuid(self, transfer_uuid: UUID) -> CarTransfer | None: ...
    
    @abstractmethod
    def get_incoming(self, user_id: int) -> list[CarTransfer]: ...
    
    @abstractmethod
    def get_outgoing(self, user_id: int) -> list[CarTransfer]: ...
    
    @abstractmethod
    def create(self, transfer: CarTransfer) -> CarTransfer: ...
    
    @abstractmethod
    def update_status(self, transfer: CarTransfer, status: str) -> None: ...
    
    @abstractmethod
    def transfer_car_ownership(self, car: Car, new_user_id: int, transfer: CarTransfer) -> None: ...
    