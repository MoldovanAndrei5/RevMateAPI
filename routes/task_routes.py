from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import Car
from models.maintenance_task import MaintenanceTask
from database import get_db
from models.user import User
from schemas.task_schema import TaskSchema, TaskCreate, TaskUpdate
from utils.auth import get_current_user

router = APIRouter(tags=["Tasks"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[TaskSchema])
def get_user_tasks(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    return db.query(MaintenanceTask).join(Car).filter(Car.user_id == user_id).all()

@router.get("/{task_uuid}", response_model=TaskSchema)
def get_task(task_uuid: str, db: Session = Depends(get_db)):
    db_task = db.query(MaintenanceTask).get(task_uuid)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/car/{car_uuid}", response_model=List[TaskSchema])
def get_car_tasks(car_uuid: str, db: Session = Depends(get_db)):
     return db.query(MaintenanceTask).filter(MaintenanceTask.car_uuid == car_uuid).all()

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = MaintenanceTask(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/{task_uuid}", response_model=TaskSchema)
def update_task(task_uuid: str, task: TaskUpdate, db: Session = Depends(get_db)):
    db_query = db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid)
    db_task = db_query.first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_query.update(task.model_dump())
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_uuid}")
def delete_task(task_uuid: str, db: Session = Depends(get_db)):
    db_query = db.query(MaintenanceTask).filter(MaintenanceTask.task_uuid == task_uuid).first()
    if not db_query:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_query)
    db.commit()
    return {"message": f"Task {task_uuid} deleted successfully"}
