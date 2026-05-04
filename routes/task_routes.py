from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.task_schema import TaskSchema, TaskCreate, TaskUpdate
from services.task_service import TaskService
from utils.auth import get_current_user

router = APIRouter(tags=["Tasks"], dependencies=[Depends(get_current_user)])

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

@router.get("/", response_model=List[TaskSchema])
def get_user_tasks(user_id: int = Depends(get_current_user), service: TaskService = Depends(get_task_service)):
    return service.get_user_tasks(user_id)

@router.get("/car/{car_uuid}", response_model=List[TaskSchema])
def get_car_tasks(car_uuid: str, service: TaskService = Depends(get_task_service)):
    return service.get_car_tasks(car_uuid)


@router.get("/{task_uuid}", response_model=TaskSchema)
def get_task(task_uuid: str, service: TaskService = Depends(get_task_service)):
    return service.get_task(task_uuid)

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task)

@router.put("/{task_uuid}", response_model=TaskSchema)
def update_task(task_uuid: str, task: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return service.update_task(task_uuid, task)

@router.delete("/{task_uuid}")
def delete_task(task_uuid: str, service: TaskService = Depends(get_task_service)):
    return service.delete_task(task_uuid)