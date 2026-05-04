from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from database import get_db
from models.invoice import Invoice
from models.maintenance_task import MaintenanceTask
from models.car import Car
from schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from utils.auth import get_current_user
from utils.s3 import generate_presigned_download_url, delete_file

router = APIRouter(tags=["Invoices"], dependencies=[Depends(get_current_user)])

def build_invoice_response(invoice: Invoice) -> InvoiceResponse:
    return InvoiceResponse(
        invoice_uuid=invoice.invoice_uuid,
        task_uuid=invoice.task_uuid,
        file_key=invoice.file_key,
        file_name=invoice.file_name,
        file_type=invoice.file_type,
        file_size=invoice.file_size,
        uploaded_at=invoice.uploaded_at,
        download_url=generate_presigned_download_url(invoice.file_key)
    )


@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    body: InvoiceCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    task = db.query(MaintenanceTask).join(Car).filter(
        MaintenanceTask.task_uuid == body.task_uuid,
        Car.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    invoice = Invoice(
        task_uuid=body.task_uuid,
        file_key=body.file_key,
        file_name=body.file_name,
        file_type=body.file_type,
        file_size=body.file_size,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return build_invoice_response(invoice)


@router.get("/task/{task_uuid}", response_model=list[InvoiceResponse])
def get_task_invoices(
    task_uuid: UUID,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    task = db.query(MaintenanceTask).join(Car).filter(
        MaintenanceTask.task_uuid == task_uuid,
        Car.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    invoices = db.query(Invoice).filter(
        Invoice.task_uuid == task_uuid
    ).all()

    return [build_invoice_response(i) for i in invoices]


@router.delete("/{invoice_uuid}")
def delete_invoice(
    invoice_uuid: UUID,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    invoice = db.query(Invoice).join(MaintenanceTask).join(Car).filter(
        Invoice.invoice_uuid == invoice_uuid,
        Car.user_id == user_id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        delete_file(invoice.file_key)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete file from storage")

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted successfully"}