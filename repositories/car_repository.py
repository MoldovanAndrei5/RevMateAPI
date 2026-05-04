from sqlalchemy.orm import Session, joinedload

from models import MaintenanceTask
from models.car import Car

class CarRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> list[Car]:
        return self.db.query(Car).filter(Car.user_id == user_id).all()

    def get_by_uuid(self, car_uuid: str, user_id: int) -> Car | None:
        return self.db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id).first()

    def create(self, car: Car) -> Car:
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
        return car

    def update(self, car_uuid: str, user_id: int, data: dict) -> Car | None:
        db_query = self.db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id)
        if not db_query.first():
            return None
        db_query.update(data)
        self.db.commit()
        return db_query.first()

    def delete(self, car: Car) -> None:
        self.db.delete(car)
        self.db.commit()

    def get_car_with_tasks_and_invoices(self, car_uuid: str) -> list[MaintenanceTask]:
        return self.db.query(MaintenanceTask).options(joinedload(MaintenanceTask.invoices)).filter(MaintenanceTask.car_uuid == car_uuid).all()