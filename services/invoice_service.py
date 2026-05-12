from fastapi import HTTPException
from uuid import UUID
from models.invoice import Invoice
from repositories.interfaces.i_invoice_repository import IInvoiceRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse, InvoiceDownloadResponse
from schemas.response_schema import MessageResponse
from services.interfaces.i_invoice_service import IInvoiceService
from utils.s3 import generate_presigned_download_url, delete_file

class InvoiceService(IInvoiceService):
    def __init__(self, repo: IInvoiceRepository, task_repo: ITaskRepository):
        self.repo = repo
        self.task_repo = task_repo
    
    def _validate_owner(self, invoice_uuid: UUID, user_id: int) -> Invoice:
        invoice = self.repo.get_by_uuid_and_user(invoice_uuid, user_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found for user")
        return invoice

    def create_invoice(self, user_id: int, data: InvoiceCreate) -> InvoiceResponse:
        task = self.task_repo.get_by_uuid_and_user(data.task_uuid, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found for user")
        invoice = Invoice(
            task_uuid=data.task_uuid,
            file_key=data.file_key,
            file_name=data.file_name,
            file_type=data.file_type,
            file_size=data.file_size,
        )
        created = self.repo.create(invoice)
        return InvoiceResponse.model_validate(created)

    def get_task_invoices(self, task_uuid: UUID, user_id: int) -> list[InvoiceResponse]:
        task = self.task_repo.get_by_uuid_and_user(task_uuid, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found for user")
        invoices = self.repo.get_by_task(task_uuid)
        return [InvoiceResponse.model_validate(i) for i in invoices]
    
    def get_invoice_download_link(self, invoice_uuid: UUID, user_id: int) -> InvoiceDownloadResponse:
        invoice = self._validate_owner(invoice_uuid, user_id)
        return InvoiceDownloadResponse(download_url=generate_presigned_download_url(invoice.file_key))

    def delete_invoice(self, invoice_uuid: UUID, user_id: int) -> MessageResponse:
        invoice = self._validate_owner(invoice_uuid, user_id)
        try:
            delete_file(invoice.file_key)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to delete file from storage")
        self.repo.delete(invoice)
        return MessageResponse(message=f"Invoice {invoice_uuid} deleted successfully")