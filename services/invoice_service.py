from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from models.invoice import Invoice
from repositories.invoice_repository import InvoiceRepository
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse, InvoiceDownloadResponse
from utils.s3 import generate_presigned_download_url, delete_file

class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)

    def _build_response(self, invoice: Invoice) -> InvoiceResponse:
        return InvoiceResponse(
            invoice_uuid=invoice.invoice_uuid,
            task_uuid=invoice.task_uuid,
            file_key=invoice.file_key,
            file_name=invoice.file_name,
            file_type=invoice.file_type,
            file_size=invoice.file_size,
            uploaded_at=invoice.uploaded_at,
        )

    def create_invoice(self, body: InvoiceCreate, user_id: int) -> InvoiceResponse:
        task = self.repo.get_task_by_uuid(body.task_uuid, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        invoice = Invoice(
            task_uuid=body.task_uuid,
            file_key=body.file_key,
            file_name=body.file_name,
            file_type=body.file_type,
            file_size=body.file_size,
        )
        created = self.repo.create(invoice)
        return self._build_response(created)

    def get_task_invoices(self, task_uuid: UUID, user_id: int) -> list[InvoiceResponse]:
        task = self.repo.get_task_by_uuid(task_uuid, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        invoices = self.repo.get_by_task(task_uuid)
        return [self._build_response(i) for i in invoices]
    
    def get_invoice_download_link(self, invoice_uuid: UUID, user_id: int) -> InvoiceDownloadResponse:
        invoice = self.repo.get_by_uuid(invoice_uuid, user_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return InvoiceDownloadResponse(download_url=generate_presigned_download_url(invoice.file_key))

    def delete_invoice(self, invoice_uuid: UUID, user_id: int) -> dict:
        print(f"[DELETE] Attempting to delete invoice {invoice_uuid} for user {user_id}")
        invoice = self.repo.get_by_uuid(invoice_uuid, user_id)
        print(f"[DELETE] Invoice found: {invoice}")
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        try:
            print(f"[DELETE] Deleting from S3: {invoice.file_key}")
            delete_file(invoice.file_key)
            print(f"[DELETE] S3 delete successful")
        except Exception as e:
            print(f"[DELETE] S3 delete failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete file from storage")
        self.repo.delete(invoice)
        print(f"[DELETE] DB delete successful")
        return {"message": "Invoice deleted successfully"}