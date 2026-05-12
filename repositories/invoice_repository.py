from uuid import UUID
from sqlalchemy.orm import Session
from models import MaintenanceTask, Car
from models.invoice import Invoice
from repositories.interfaces.i_invoice_repository import IInvoiceRepository

class InvoiceRepository(IInvoiceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_uuid(self, invoice_uuid: UUID) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.invoice_uuid == invoice_uuid).first()

    def get_by_task(self, task_uuid: UUID) -> list[Invoice]:
        return self.db.query(Invoice).filter(Invoice.task_uuid == task_uuid).all()

    def get_by_uuid_and_user(self, invoice_uuid: UUID, user_id: int) -> Invoice | None:
        return self.db.query(Invoice) \
            .join(MaintenanceTask, Invoice.task_uuid == MaintenanceTask.task_uuid) \
            .join(Car, MaintenanceTask.car_uuid == Car.car_uuid) \
            .filter(Invoice.invoice_uuid == invoice_uuid, Car.user_id == user_id).first()

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice: Invoice) -> None:
        self.db.delete(invoice)
        self.db.commit()