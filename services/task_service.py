from uuid import UUID
from fastapi import HTTPException
from models.maintenance_task import MaintenanceTask
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from schemas.response_schema import MessageResponse
from schemas.task_schema import TaskCreate, TaskUpdate, TaskSchema
from services.interfaces.i_task_service import ITaskService
from utils.s3 import delete_file

class TaskService(ITaskService):
    def __init__(self, repo: ITaskRepository, car_repo: ICarRepository):
        self.repo = repo
        self.car_repo = car_repo
        
    def _validate_owner(self, task_uuid: UUID, user_id: int) -> MaintenanceTask:
        task = self.repo.get_by_uuid_and_user(task_uuid, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found for user")
        return task

    def get_user_tasks(self, user_id: int) -> list[TaskSchema]:
        tasks = self.repo.get_all_by_user(user_id)
        return [TaskSchema.model_validate(task) for task in tasks]

    def get_task(self, task_uuid: UUID, user_id: int) -> TaskSchema:
        task = self._validate_owner(task_uuid, user_id)
        return TaskSchema.model_validate(task)

    def get_car_tasks(self, car_uuid: UUID, user_id: int) -> list[TaskSchema]:
        car = self.car_repo.get_by_uuid(car_uuid)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        if car.user_id != user_id:
            raise HTTPException(status_code=403, detail="Car does not belong to user")
        tasks = self.repo.get_by_car(car_uuid)
        return [TaskSchema.model_validate(task) for task in tasks]

    def create_task(self, user_id: int, data: TaskCreate) -> TaskSchema:
        car = self.car_repo.get_by_uuid(data.car_uuid)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        if car.user_id != user_id:
            raise HTTPException(status_code=403, detail="Car does not belong to user")
        task = MaintenanceTask(**data.model_dump())
        created = self.repo.create(task)
        return TaskSchema.model_validate(created)

    def update_task(self, task_uuid: UUID, user_id: int, data: TaskUpdate) -> TaskSchema:
        self._validate_owner(task_uuid, user_id)
        updated = self.repo.update(task_uuid, data.model_dump(exclude_none=True))
        return TaskSchema.model_validate(updated)

    def delete_task(self, task_uuid: UUID, user_id: int) -> MessageResponse:
        task = self._validate_owner(task_uuid, user_id)
        for invoice in task.invoices:
            try:
                delete_file(invoice.file_key)
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to delete file from storage")
        self.repo.delete(task)
        return MessageResponse(message=f"Task {task_uuid} deleted successfully")