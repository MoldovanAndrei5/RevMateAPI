from abc import ABC, abstractmethod
from uuid import UUID
from models import MaintenanceTask

class ITaskRepository(ABC):
    @abstractmethod
    def get_all_by_user(self, user_id: int) -> list[MaintenanceTask]: ...
    
    @abstractmethod
    def get_by_uuid(self, task_uuid: UUID) -> MaintenanceTask | None: ...
    
    @abstractmethod
    def get_by_uuid_and_user(self, task_uuid: UUID, user_id: int) -> MaintenanceTask | None: ...
    
    @abstractmethod
    def get_by_car(self, car_uuid: UUID) -> list[MaintenanceTask]: ...

    @abstractmethod
    def get_by_car_with_invoices(self, car_uuid: UUID) -> list[MaintenanceTask]: ...
    
    @abstractmethod
    def create(self, task: MaintenanceTask) -> MaintenanceTask: ...
    
    @abstractmethod
    def update(self, task_uuid: UUID, data: dict) -> MaintenanceTask | None: ...
    
    @abstractmethod
    def delete(self, task: MaintenanceTask) -> None: ...