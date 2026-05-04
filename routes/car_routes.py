from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from schemas.car_schema import CarSchema, CarCreate, CarUpdate
from services.car_service import CarService
from utils.auth import get_current_user

router = APIRouter(tags=["Cars"])

def get_car_service(db: Session = Depends(get_db)) -> CarService:
    return CarService(db)

@router.get("/", response_model=List[CarSchema])
def get_user_cars(user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    return service.get_user_cars(user_id)


@router.get("/{car_uuid}", response_model=CarSchema)
def get_car(car_uuid: str, user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    return service.get_car(car_uuid, user_id)


@router.post("/", response_model=CarSchema)
def create_car(car: CarCreate, user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    return service.create_car(car, user_id)


@router.put("/{car_uuid}", response_model=CarSchema)
def update_car(car_uuid: str, car_data: CarUpdate, user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    return service.update_car(car_uuid, user_id, car_data)


@router.delete("/{car_uuid}")
def delete_car(car_uuid: str, user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    return service.delete_car(car_uuid, user_id)


@router.get("/{car_uuid}/report")
def get_car_report(car_uuid: str, user_id: int = Depends(get_current_user), service: CarService = Depends(get_car_service)):
    pdf_bytes, filename = service.generate_report(car_uuid, user_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )