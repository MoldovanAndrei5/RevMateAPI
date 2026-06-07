from fastapi import HTTPException
from uuid import UUID

from models import MaintenanceTask
from models.invoice import Invoice
from repositories.interfaces.i_invoice_repository import IInvoiceRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse, InvoiceDownloadResponse
from services.interfaces.i_invoice_service import IInvoiceService
from utils.s3 import generate_presigned_download_url, delete_file
from utils.logger import get_logger


logger = get_logger(__name__)

class InvoiceService(IInvoiceService):
    def __init__(self, repo: IInvoiceRepository, task_repo: ITaskRepository):
        self.repo = repo
        self.task_repo = task_repo
    
    def _validate_owner(self, invoice_uuid: UUID, user_id: int) -> Invoice:
        invoice = self.repo.get_by_uuid_and_user(invoice_uuid, user_id)
        if not invoice:
            logger.warning(f"Invoice {invoice_uuid} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Invoice not found for user")
        return invoice

    def _validate_task_owner(self, task_uuid: UUID, user_id: int) -> None:
        task = self.task_repo.get_by_uuid_and_user(task_uuid, user_id)
        if not task:
            logger.warning(f"Task {task_uuid} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Task not found for user")

    def create_invoice(self, user_id: int, data: InvoiceCreate) -> InvoiceResponse:
        logger.info(f"Creating invoice for task {data.task_uuid} and user {user_id}")
        self._validate_task_owner(data.task_uuid, user_id)
        invoice = Invoice(
            task_uuid=data.task_uuid,
            file_key=data.file_key,
            file_name=data.file_name,
            file_type=data.file_type,
            file_size=data.file_size,
        )
        created = self.repo.create(invoice)
        logger.info(f"Created invoice {created.invoice_uuid}")
        return InvoiceResponse.model_validate(created)

    def get_task_invoices(self, task_uuid: UUID, user_id: int) -> list[InvoiceResponse]:
        logger.info(f"Getting invoices for task {task_uuid} and user {user_id}")
        self._validate_task_owner(task_uuid, user_id)
        invoices = self.repo.get_by_task(task_uuid)
        return [InvoiceResponse.model_validate(i) for i in invoices]
    
    def get_invoice_download_link(self, invoice_uuid: UUID, user_id: int) -> InvoiceDownloadResponse:
        logger.info(f"Getting download link for invoice {invoice_uuid} and user {user_id}")
        invoice = self._validate_owner(invoice_uuid, user_id)
        return InvoiceDownloadResponse(download_url=generate_presigned_download_url(invoice.file_key))

    def delete_invoice(self, invoice_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Deleting invoice {invoice_uuid} for user {user_id}")
        invoice = self._validate_owner(invoice_uuid, user_id)
        try:
            delete_file(invoice.file_key)
        except Exception as e:
            logger.error(f"Failed to delete file {invoice.file_key}: {e}")
        self.repo.delete(invoice)
        logger.info(f"Deleted invoice {invoice_uuid}")
        return {"message": f"Invoice {invoice_uuid} deleted successfully"}