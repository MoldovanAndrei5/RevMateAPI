from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.car import Car
from repositories.car_repository import CarRepository
from schemas.car_schema import CarCreate, CarUpdate
from utils.pdf_generator import generate_car_report

class CarService:
    def __init__(self, db: Session):
        self.repo = CarRepository(db)
        self.db = db

    def get_user_cars(self, user_id: int) -> list[Car]:
        return self.repo.get_all_by_user(user_id)

    def get_car(self, car_uuid: str, user_id: int) -> Car:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

    def create_car(self, data: CarCreate, user_id: int) -> Car:
        car = Car(**data.model_dump(), user_id=user_id)
        return self.repo.create(car)

    def update_car(self, car_uuid: str, user_id: int, data: CarUpdate) -> Car:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        updated = self.repo.update(car_uuid, user_id, data.model_dump())
        return updated

    def delete_car(self, car_uuid: str, user_id: int) -> dict:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        self.repo.delete(car)
        return {"message": f"Car {car_uuid} deleted successfully"}

    def generate_report(self, car_uuid: str, user_id: int) -> tuple[bytes, str]:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        tasks = self.repo.get_car_with_tasks_and_invoices(car_uuid)
        pdf_bytes = generate_car_report(car, tasks)
        filename = f"revmate_{car.make}_{car.model}_{car.year}_report.pdf".replace(" ", "_")
        return pdf_bytes, filename