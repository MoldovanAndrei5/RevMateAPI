from abc import ABC, abstractmethod
from schemas.task_schema import TaskSuggestionRequest, TaskSuggestionResponse

class IAIProxyService(ABC):
    @abstractmethod
    def get_suggestions(self, body: TaskSuggestionRequest) -> list[TaskSuggestionResponse]: ...
