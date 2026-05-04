from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.maintenance_task import MaintenanceTask
from repositories.task_repository import TaskRepository
from schemas.task_schema import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def get_user_tasks(self, user_id: int) -> list[MaintenanceTask]:
        return self.repo.get_all_by_user(user_id)

    def get_task(self, task_uuid: str) -> MaintenanceTask:
        task = self.repo.get_by_uuid(task_uuid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def get_car_tasks(self, car_uuid: str) -> list[MaintenanceTask]:
        return self.repo.get_by_car(car_uuid)

    def create_task(self, data: TaskCreate) -> MaintenanceTask:
        task = MaintenanceTask(**data.model_dump())
        return self.repo.create(task)

    def update_task(self, task_uuid: str, data: TaskUpdate) -> MaintenanceTask:
        task = self.repo.get_by_uuid(task_uuid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        updated = self.repo.update(task_uuid, data.model_dump())
        return updated

    def delete_task(self, task_uuid: str) -> dict:
        task = self.repo.get_by_uuid(task_uuid)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        self.repo.delete(task)
        return {"message": f"Task {task_uuid} deleted successfully"}