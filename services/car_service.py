from uuid import UUID
from fastapi import HTTPException
from models.car import Car
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from schemas.car_schema import CarCreate, CarUpdate, CarSchema
from services.interfaces.i_car_service import ICarService
from utils.pdf_generator import generate_car_report
from utils.s3 import generate_presigned_download_url, delete_file
from utils.logger import get_logger


logger = get_logger(__name__)

class CarService(ICarService):
    def __init__(self, repo: ICarRepository, task_repo: ITaskRepository):
        self.repo = repo
        self.task_repo = task_repo

    def _to_schema(self, car: Car) -> CarSchema:
        return CarSchema(
            **{k: v for k, v in car.__dict__.items() if not k.startswith('_')},
            image_url=generate_presigned_download_url(car.image_key, expires_in=604800) if car.image_key else None
        )
    
    def _validate_owner(self, car_uuid: UUID, user_id: int) -> Car:
        car = self.repo.get_by_uuid(car_uuid)
        if not car:
            logger.warning(f"Car {car_uuid} not found")
            raise HTTPException(status_code=404, detail="Car not found for user")
        if car.user_id != user_id:
            logger.warning(f"Car {car_uuid} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Car does not belong to user")
        return car

    def get_user_cars(self, user_id: int) -> list[CarSchema]:
        logger.info(f"Getting cars for user {user_id}")
        cars = self.repo.get_all_by_user(user_id)
        return [self._to_schema(car) for car in cars]

    def get_car(self, car_uuid: UUID, user_id: int) -> CarSchema:
        logger.info(f"Getting car {car_uuid} for user {user_id}")
        car = self._validate_owner(car_uuid, user_id)
        return self._to_schema(car)

    def create_car(self, user_id: int, data: CarCreate) -> CarSchema:
        logger.info(f"Creating car for user {user_id}")
        car = Car(**data.model_dump(), user_id=user_id)
        created = self.repo.create(car)
        logger.info(f"Created car {created.car_uuid}")
        return self._to_schema(created)

    def update_car(self, car_uuid: UUID, user_id: int, data: CarUpdate) -> CarSchema:
        logger.info(f"Updating car {car_uuid} for user {user_id}")
        car = self._validate_owner(car_uuid, user_id)
        if data.image_key is not None and car.image_key is not None and data.image_key != car.image_key:
            try:
                delete_file(car.image_key)
            except Exception as e:
                logger.error(f"Failed to delete file {car.image_key}: {e}")
        updated = self.repo.update(car_uuid, data.model_dump(exclude_none=True))
        logger.info(f"Updated car {car_uuid}")
        return self._to_schema(updated)

    def delete_car(self, car_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Deleting car {car_uuid} for user {user_id}")
        car = self._validate_owner(car_uuid, user_id)
        tasks = self.task_repo.get_by_car_with_invoices(car_uuid)
        for task in tasks:
            for invoice in task.invoices:
                try:
                    delete_file(invoice.file_key)
                except Exception as e:
                    logger.error(f"Failed to delete file {invoice.file_key}: {e}")
        if car.image_key is not None:
            try:
                delete_file(car.image_key)
            except Exception as e:
                logger.error(f"Failed to delete file {car.image_key}: {e}")
        self.repo.delete(car)
        logger.info(f"Deleted car {car_uuid}")
        return {"message": f"Car {car_uuid} deleted successfully"}

    def generate_report(self, car_uuid: UUID, user_id: int) -> tuple[bytes, str]:
        logger.info(f"Generating report for user {user_id} and car {car_uuid}")
        car = self._validate_owner(car_uuid, user_id)
        tasks = self.task_repo.get_by_car_with_invoices(car_uuid)
        pdf_bytes = generate_car_report(car, tasks)
        filename = f"revmate_{car.make}_{car.model}_{car.year}_report.pdf".replace(" ", "_")
        logger.info(f"Generated report for user {user_id} and car {car_uuid}")
        return pdf_bytes, filename