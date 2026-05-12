from abc import ABC, abstractmethod
from uuid import UUID
from models.invoice import Invoice

class IInvoiceRepository(ABC):
    @abstractmethod
    def get_by_uuid(self, invoice_uuid: UUID) -> Invoice | None: ...
    
    @abstractmethod
    def get_by_task(self, task_uuid: UUID) -> list[Invoice]: ...
    
    @abstractmethod
    def get_by_uuid_and_user(self, invoice_uuid: UUID, user_id: int) -> Invoice | None: ...
    
    @abstractmethod
    def create(self, invoice: Invoice) -> Invoice: ...
    
    @abstractmethod
    def delete(self, invoice: Invoice) -> None: ...