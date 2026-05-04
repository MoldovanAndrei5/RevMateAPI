from sqlalchemy.orm import Session
from models.car import Car
from models.maintenance_task import MaintenanceTask

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask).join(Car).filter(Car.user_id == user_id).all()

    def get_by_uuid(self, task_uuid: str) -> MaintenanceTask | None:
        return self.db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid).first()

    def get_by_car(self, car_uuid: str) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask).filter(MaintenanceTask.car_uuid == car_uuid).all()

    def create(self, task: MaintenanceTask) -> MaintenanceTask:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task_uuid: str, data: dict) -> MaintenanceTask | None:
        db_query = self.db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid)
        if not db_query.first():
            return None
        db_query.update(data)
        self.db.commit()
        return db_query.first()

    def delete(self, task: MaintenanceTask) -> None:
        self.db.delete(task)
        self.db.commit()