from uuid import UUID
from fastapi import APIRouter, Depends
from dependencies.di import get_task_service
from schemas.response_schema import MessageResponse
from schemas.task_schema import TaskSchema, TaskCreate, TaskUpdate
from services.interfaces.i_task_service import ITaskService
from utils.auth import get_current_user

router = APIRouter(tags=["Tasks"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[TaskSchema])
def get_user_tasks(user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.get_user_tasks(user_id)

@router.get("/car/{car_uuid}", response_model=list[TaskSchema])
def get_car_tasks(car_uuid: UUID, user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.get_car_tasks(car_uuid, user_id)

@router.get("/{task_uuid}", response_model=TaskSchema)
def get_task(task_uuid: UUID, user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.get_task(task_uuid, user_id)

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.create_task(user_id, task)

@router.put("/{task_uuid}", response_model=TaskSchema)
def update_task(task_uuid: UUID, task: TaskUpdate, user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.update_task(task_uuid, user_id, task)

@router.delete("/{task_uuid}", response_model=MessageResponse)
def delete_task(task_uuid: UUID, user_id: int = Depends(get_current_user), task_service: ITaskService = Depends(get_task_service)):
    return task_service.delete_task(task_uuid, user_id)