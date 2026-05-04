from sqlalchemy.orm import Session, joinedload
from models.car_transfer import CarTransfer
from models.car import Car
from models.user import User

class TransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_receiver_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_car_by_uuid(self, car_uuid: str, user_id: int) -> Car | None:
        return self.db.query(Car).filter(Car.car_uuid == car_uuid, Car.user_id == user_id).first()

    def get_pending_by_car(self, car_uuid: str) -> CarTransfer | None:
        return self.db.query(CarTransfer).filter(CarTransfer.car_uuid == car_uuid, CarTransfer.status == "pending").first()

    def get_incoming(self, user_id: int) -> list[CarTransfer]:
        return (self.db.query(CarTransfer).options(
            joinedload(CarTransfer.sender),
            joinedload(CarTransfer.car)).filter(CarTransfer.receiver_user_id == user_id, CarTransfer.status == "pending").all())

    def get_outgoing(self, user_id: int) -> list[CarTransfer]:
        return self.db.query(CarTransfer).options(
            joinedload(CarTransfer.receiver),
            joinedload(CarTransfer.car)).filter(CarTransfer.sender_user_id == user_id, CarTransfer.status == "pending").all()

    def get_by_uuid_and_receiver(self, transfer_uuid: str, user_id: int) -> CarTransfer | None:
        return self.db.query(CarTransfer).options(
            joinedload(CarTransfer.car)).filter(CarTransfer.transfer_uuid == transfer_uuid, CarTransfer.receiver_user_id == user_id, CarTransfer.status == "pending").first()

    def get_by_uuid_and_sender(self, transfer_uuid: str, user_id: int) -> CarTransfer | None:
        return self.db.query(CarTransfer).filter(CarTransfer.transfer_uuid == transfer_uuid, CarTransfer.sender_user_id == user_id, CarTransfer.status == "pending").first()

    def create(self, transfer: CarTransfer) -> CarTransfer:
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def update_status(self, transfer: CarTransfer, status: str) -> None:
        transfer.status = status
        self.db.commit()

    def transfer_car_ownership(self, car: Car, new_user_id: int, transfer: CarTransfer) -> None:
        car.user_id = new_user_id
        transfer.status = "accepted"
        self.db.commit()