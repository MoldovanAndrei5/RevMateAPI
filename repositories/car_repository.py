from uuid import UUID
from sqlalchemy.orm import Session
from models.car import Car
from repositories.interfaces.i_car_repository import ICarRepository

class CarRepository(ICarRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> list[Car]:
        return self.db.query(Car).filter(Car.user_id == user_id).all()

    def get_by_uuid(self, car_uuid: UUID) -> Car | None:
        return self.db.query(Car).filter(Car.car_uuid == car_uuid).first()

    def create(self, car: Car) -> Car:
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
        return car

    def update(self, car_uuid: UUID, data: dict) -> Car | None:
        car = self.get_by_uuid(car_uuid)
        for key, value in data.items():
            setattr(car, key, value)
        self.db.commit()
        self.db.refresh(car)
        return car

    def delete(self, car: Car) -> None:
        self.db.delete(car)
        self.db.commit()
    