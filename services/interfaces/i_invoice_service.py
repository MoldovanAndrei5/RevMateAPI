from abc import ABC, abstractmethod
from uuid import UUID
from schemas.invoice_schema import InvoiceDownloadResponse, InvoiceResponse, InvoiceCreate
from schemas.response_schema import MessageResponse

class IInvoiceService(ABC):
    @abstractmethod
    def create_invoice(self, data: InvoiceCreate, user_id: int) -> InvoiceResponse: ...
    
    @abstractmethod
    def get_task_invoices(self, task_uuid: UUID, user_id: int) -> list[InvoiceResponse]: ...
    
    @abstractmethod
    def get_invoice_download_link(self, invoice_uuid: UUID, user_id: int) -> InvoiceDownloadResponse: ...
    
    @abstractmethod
    def delete_invoice(self, invoice_uuid: UUID, user_id: int) -> MessageResponse: ...
