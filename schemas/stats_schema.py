from pydantic import BaseModel


class MonthlyStats(BaseModel):
    month: str        # Jan 2025
    completed: int
    scheduled: int

class StatsResponse(BaseModel):
    total_spent: float
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    spent_by_category: dict[str, float]
    tasks_by_month: list[MonthlyStats]