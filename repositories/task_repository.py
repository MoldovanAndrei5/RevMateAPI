from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from models.car import Car
from models.maintenance_task import MaintenanceTask
from repositories.interfaces.i_task_repository import ITaskRepository

class TaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask).join(Car).filter(Car.user_id == user_id).all()

    def get_by_uuid(self, task_uuid: UUID) -> MaintenanceTask | None:
        return self.db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid).first()
    
    def get_by_uuid_and_user(self, task_uuid: UUID, user_id: int) -> MaintenanceTask | None:
        return self.db.query(MaintenanceTask)\
            .options(joinedload(MaintenanceTask.invoices))\
            .join(Car, MaintenanceTask.car_uuid == Car.car_uuid)\
            .filter(MaintenanceTask.task_uuid == task_uuid, Car.user_id == user_id).first()

    def get_by_car(self, car_uuid: UUID) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask).filter(MaintenanceTask.car_uuid == car_uuid).all()

    def get_by_car_with_invoices(self, car_uuid: UUID) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask)\
            .options(joinedload(MaintenanceTask.invoices))\
            .filter(MaintenanceTask.car_uuid == car_uuid).all()

    def create(self, task: MaintenanceTask) -> MaintenanceTask:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task_uuid: UUID, data: dict) -> MaintenanceTask | None:
        task = self.db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid).first()
        if not task:
            return None
        for key, value in data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: MaintenanceTask) -> None:
        self.db.delete(task)
        self.db.commit()