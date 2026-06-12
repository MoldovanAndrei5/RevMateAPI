from fastapi import APIRouter, Depends
from uuid import UUID
from dependencies.di import get_invoice_service
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse, InvoiceDownloadResponse
from schemas.response_schema import MessageResponse
from services.interfaces.i_invoice_service import IInvoiceService
from utils.auth import get_current_user

router = APIRouter(tags=["Invoices"], dependencies=[Depends(get_current_user)])

@router.post("/", response_model=InvoiceResponse)
def create_invoice(body: InvoiceCreate, user_id: int = Depends(get_current_user), invoice_service: IInvoiceService = Depends(get_invoice_service)):
    return invoice_service.create_invoice(user_id, body)

@router.get("/task/{task_uuid}", response_model=list[InvoiceResponse])
def get_task_invoices(task_uuid: UUID, user_id: int = Depends(get_current_user), invoice_service: IInvoiceService = Depends(get_invoice_service)):
    return invoice_service.get_task_invoices(task_uuid, user_id)

@router.get("/{invoice_uuid}/download", response_model=InvoiceDownloadResponse)
def get_invoice_download_link(invoice_uuid: UUID, user_id = Depends(get_current_user), invoice_service: IInvoiceService = Depends(get_invoice_service)):
    return invoice_service.get_invoice_download_link(invoice_uuid, user_id)

@router.delete("/{invoice_uuid}", response_model=MessageResponse)
def delete_invoice(invoice_uuid: UUID, user_id: int = Depends(get_current_user), invoice_service: IInvoiceService = Depends(get_invoice_service)):
    return invoice_service.delete_invoice(invoice_uuid, user_id)