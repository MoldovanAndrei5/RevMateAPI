from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from services.invoice_service import InvoiceService
from utils.auth import get_current_user

router = APIRouter(tags=["Invoices"], dependencies=[Depends(get_current_user)])

def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)

@router.post("/", response_model=InvoiceResponse)
def create_invoice(body: InvoiceCreate, user_id: int = Depends(get_current_user), service: InvoiceService = Depends(get_invoice_service)):
    return service.create_invoice(body, user_id)

@router.get("/task/{task_uuid}", response_model=list[InvoiceResponse])
def get_task_invoices(task_uuid: UUID, user_id: int = Depends(get_current_user), service: InvoiceService = Depends(get_invoice_service)):
    return service.get_task_invoices(task_uuid, user_id)

@router.delete("/{invoice_uuid}")
def delete_invoice(invoice_uuid: UUID, user_id: int = Depends(get_current_user), service: InvoiceService = Depends(get_invoice_service)):
    return service.delete_invoice(invoice_uuid, user_id)