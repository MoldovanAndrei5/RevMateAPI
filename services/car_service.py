from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.car import Car
from repositories.car_repository import CarRepository
from schemas.car_schema import CarCreate, CarUpdate, CarSchema
from utils.pdf_generator import generate_car_report
from utils.s3 import generate_presigned_download_url, delete_file


class CarService:
    def __init__(self, db: Session):
        self.repo = CarRepository(db)
        self.db = db

    def _to_schema(self, car: Car) -> CarSchema:
        return CarSchema(
            **{k: v for k, v in car.__dict__.items() if not k.startswith('_')},
            image_url=generate_presigned_download_url(car.image_key, expires_in=604800) if car.image_key else None
        )

    def get_user_cars(self, user_id: int) -> list[CarSchema]:
        cars = self.repo.get_all_by_user(user_id)
        return [self._to_schema(car) for car in cars]

    def get_car(self, car_uuid: str, user_id: int) -> CarSchema:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return self._to_schema(car)

    def create_car(self, data: CarCreate, user_id: int) -> CarSchema:
        car = Car(**data.model_dump(), user_id=user_id)
        return self.repo.create(car)

    def update_car(self, car_uuid: str, user_id: int, data: CarUpdate) -> CarSchema:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        if data.image_key is not None and car.image_key is not None and data.image_key != car.image_key:
            try:
                delete_file(car.image_key)
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to delete old image")
        updated = self.repo.update(car_uuid, user_id, data.model_dump())
        return updated

    def delete_car(self, car_uuid: str, user_id: int) -> dict:
        car = self.repo.get_by_uuid(car_uuid, user_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        tasks = self.repo.get_car_with_tasks_and_invoices(car_uuid)
        for task in tasks:
            for invoice in task.invoices:
                try:
                    delete_file(invoice.file_key)
                except Exception:
                    raise HTTPException(status_code=500, detail="Failed to delete file from storage")
        if car.image_key is not None:
            try:
                delete_file(car.image_key)
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to delete file from storage")
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