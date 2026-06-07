from uuid import UUID
from fastapi import HTTPException
from models.maintenance_task import MaintenanceTask
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from schemas.task_schema import TaskCreate, TaskUpdate, TaskSchema
from services.interfaces.i_task_service import ITaskService
from utils.s3 import delete_file
from utils.logger import get_logger


logger = get_logger(__name__)

class TaskService(ITaskService):
    def __init__(self, repo: ITaskRepository, car_repo: ICarRepository):
        self.repo = repo
        self.car_repo = car_repo
        
    def _validate_owner(self, task_uuid: UUID, user_id: int) -> MaintenanceTask:
        task = self.repo.get_by_uuid_and_user(task_uuid, user_id)
        if not task:
            logger.warning(f"Task {task_uuid} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Task not found for user")
        return task
    
    def _validate_car_owner(self, car_uuid: UUID, user_id: int) -> None:
        car = self.car_repo.get_by_uuid(car_uuid)
        if not car:
            logger.warning(f"Car {car_uuid} not found")
            raise HTTPException(status_code=404, detail="Car not found")
        if car.user_id != user_id:
            logger.warning(f"Car {car_uuid} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Car does not belong to user")

    def get_user_tasks(self, user_id: int) -> list[TaskSchema]:
        logger.info(f"Getting tasks for user {user_id}")
        tasks = self.repo.get_all_by_user(user_id)
        return [TaskSchema.model_validate(task) for task in tasks]

    def get_task(self, task_uuid: UUID, user_id: int) -> TaskSchema:
        logger.info(f"Getting task {task_uuid} for user {user_id}")
        task = self._validate_owner(task_uuid, user_id)
        return TaskSchema.model_validate(task)

    def get_car_tasks(self, car_uuid: UUID, user_id: int) -> list[TaskSchema]:
        logger.info(f"Getting tasks for car {car_uuid} and user {user_id}")
        self._validate_car_owner(car_uuid, user_id)
        tasks = self.repo.get_by_car(car_uuid)
        return [TaskSchema.model_validate(task) for task in tasks]

    def create_task(self, user_id: int, data: TaskCreate) -> TaskSchema:
        logger.info(f"Creating task for car {data.car_uuid} and user {user_id}")
        self._validate_car_owner(data.car_uuid, user_id)
        task = MaintenanceTask(**data.model_dump())
        created = self.repo.create(task)
        logger.info(f"Created task {created.task_uuid}")
        return TaskSchema.model_validate(created)

    def update_task(self, task_uuid: UUID, user_id: int, data: TaskUpdate) -> TaskSchema:
        logger.info(f"Updating task {task_uuid} for user {user_id}")
        self._validate_owner(task_uuid, user_id)
        updated = self.repo.update(task_uuid, data.model_dump(exclude_none=True))
        logger.info(f"Updated task {updated.task_uuid}")
        return TaskSchema.model_validate(updated)

    def delete_task(self, task_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Deleting task {task_uuid} for user {user_id}")
        task = self._validate_owner(task_uuid, user_id)
        for invoice in task.invoices:
            try:
                delete_file(invoice.file_key)
            except Exception as e:
                logger.error(f"Failed to delete file {invoice.file_key}: {e}")
        self.repo.delete(task)
        logger.info(f"Deleted task {task_uuid}")
        return {"message": f"Task {task_uuid} deleted successfully"}
