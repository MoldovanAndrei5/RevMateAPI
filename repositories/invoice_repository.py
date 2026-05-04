from sqlalchemy.orm import Session
from models.invoice import Invoice
from models.maintenance_task import MaintenanceTask
from models.car import Car

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_task_by_uuid(self, task_uuid, user_id: int) -> MaintenanceTask | None:
        return self.db.query(MaintenanceTask).join(Car).filter(MaintenanceTask.task_uuid == task_uuid, Car.user_id == user_id).first()

    def get_by_uuid(self, invoice_uuid, user_id: int) -> Invoice | None:
        return self.db.query(Invoice).join(MaintenanceTask).join(Car).filter(Invoice.invoice_uuid == invoice_uuid, Car.user_id == user_id).first()

    def get_by_task(self, task_uuid) -> list[Invoice]:
        return self.db.query(Invoice).filter(Invoice.task_uuid == task_uuid).all()

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice: Invoice) -> None:
        self.db.delete(invoice)
        self.db.commit()