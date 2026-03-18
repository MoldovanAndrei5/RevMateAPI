from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.car_schema import CarSchema, CarCreate, CarUpdate
from models.car import Car
from database import get_db
from utils.auth import get_current_user

router = APIRouter(tags=["Cars"])

@router.get("/", response_model=List[CarSchema])
def get_user_cars(db: Session = Depends(get_db), user_id: int  = Depends(get_current_user)):
    return db.query(Car).filter(Car.user_id == user_id).all()


@router.get("/{car_uuid}", response_model=CarSchema)
def get_car(car_uuid: str, db: Session = Depends(get_db), user_id: int  = Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


@router.post("/", response_model=CarSchema)
def create_car(car: CarCreate, db: Session = Depends(get_db), user_id: int  = Depends(get_current_user)):
    new_car = Car(**car.model_dump(), user_id = user_id)
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


@router.put("/{car_uuid}", response_model=CarSchema)
def update_car(car_uuid: str, car_data: CarUpdate, db: Session = Depends(get_db), user_id: int  = Depends(get_current_user)):
    db_query = db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id)
    db_car = db_query.first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_query.update(car_data.model_dump())
    db.commit()
    db.refresh(db_car)
    return db_car


@router.delete("/{car_uuid}")
def delete_car(car_uuid: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(db_car)
    db.commit()
    return {
        "message": f"Car {car_uuid} deleted successfully"
    }