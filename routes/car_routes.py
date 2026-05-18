from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from dependencies.di import get_car_service
from schemas.car_schema import CarSchema, CarCreate, CarUpdate
from schemas.response_schema import MessageResponse
from services.interfaces.i_car_service import ICarService
from utils.auth import get_current_user

router = APIRouter(tags=["Cars"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[CarSchema])
def get_user_cars(user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    return car_service.get_user_cars(user_id)

@router.get("/{car_uuid}", response_model=CarSchema)
def get_car(car_uuid: UUID, user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    return car_service.get_car(car_uuid, user_id)

@router.post("/", response_model=CarSchema)
def create_car(car: CarCreate, user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    return car_service.create_car(user_id, car)

@router.put("/{car_uuid}", response_model=CarSchema)
def update_car(car_uuid: UUID, car_data: CarUpdate, user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    return car_service.update_car(car_uuid, user_id, car_data)

@router.delete("/{car_uuid}", response_model=MessageResponse)
def delete_car(car_uuid: UUID, user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    return car_service.delete_car(car_uuid, user_id)

@router.get("/{car_uuid}/report", response_class=Response)
def get_car_report(car_uuid: UUID, user_id: int = Depends(get_current_user), car_service: ICarService = Depends(get_car_service)):
    pdf_bytes, filename = car_service.generate_report(car_uuid, user_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )