from abc import ABC, abstractmethod
from uuid import UUID
from schemas.car_transfer_schema import CarTransferOutgoingResponse, CarTransferIncomingResponse, CarTransferInitiate


class ITransferService(ABC):
    @abstractmethod
    def initiate_transfer(self, body: CarTransferInitiate, user_id: int) -> CarTransferOutgoingResponse: ...
    
    @abstractmethod
    def get_incoming(self, user_id: int) -> list[CarTransferIncomingResponse]: ...
    
    @abstractmethod
    def get_outgoing(self, user_id: int) -> list[CarTransferOutgoingResponse]: ...
    
    @abstractmethod
    def accept_transfer(self, transfer_uuid: UUID, user_id: int) -> dict: ...
    
    @abstractmethod
    def reject_transfer(self, transfer_uuid: UUID, user_id: int) -> dict: ...
    
    @abstractmethod
    def cancel_transfer(self, transfer_uuid: UUID, user_id: int) -> dict: ...
