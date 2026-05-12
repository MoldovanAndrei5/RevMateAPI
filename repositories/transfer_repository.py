from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from models.car_transfer import CarTransfer
from models.car import Car
from repositories.interfaces.i_transfer_repository import ITransferRepository

class TransferRepository(ITransferRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_pending_by_car(self, car_uuid: UUID) -> CarTransfer | None:
        return self.db.query(CarTransfer).filter(CarTransfer.car_uuid == car_uuid, CarTransfer.status == "pending").first()
    
    def get_pending_by_uuid(self, transfer_uuid: UUID) -> CarTransfer | None:
        return self.db.query(CarTransfer)\
            .options(joinedload(CarTransfer.car))\
            .filter(CarTransfer.transfer_uuid == transfer_uuid, CarTransfer.status == "pending").first()

    def get_incoming(self, user_id: int) -> list[CarTransfer]:
        return self.db.query(CarTransfer)\
            .options(joinedload(CarTransfer.sender),joinedload(CarTransfer.car))\
            .filter(CarTransfer.receiver_user_id == user_id, CarTransfer.status == "pending").all()

    def get_outgoing(self, user_id: int) -> list[CarTransfer]:
        return self.db.query(CarTransfer)\
            .options(joinedload(CarTransfer.receiver),joinedload(CarTransfer.car))\
            .filter(CarTransfer.sender_user_id == user_id, CarTransfer.status == "pending").all()

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