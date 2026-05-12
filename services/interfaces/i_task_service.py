from abc import ABC, abstractmethod
from uuid import UUID
from schemas.response_schema import MessageResponse
from schemas.task_schema import TaskSchema, TaskUpdate, TaskCreate

class ITaskService(ABC):
    @abstractmethod
    def get_user_tasks(self, user_id: int) -> list[TaskSchema]: ...
    
    @abstractmethod
    def get_task(self, task_uuid: UUID, user_id: int) -> TaskSchema: ...
    
    @abstractmethod
    def get_car_tasks(self, car_uuid: UUID, user_id: int) -> list[TaskSchema]: ...
    
    @abstractmethod
    def create_task(self, user_id: int, data: TaskCreate) -> TaskSchema: ...
    
    @abstractmethod
    def update_task(self, task_uuid: UUID, user_id: int, data: TaskUpdate) -> TaskSchema: ...
    
    @abstractmethod
    def delete_task(self, task_uuid: UUID, user_id: int) -> MessageResponse: ...
