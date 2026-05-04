import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.car_transfer import CarTransfer
from repositories.transfer_repository import TransferRepository
from schemas.car_transfer_schema import CarTransferInitiate, CarTransferIncomingResponse, CarTransferOutgoingResponse

class TransferService:
    def __init__(self, db: Session):
        self.repo = TransferRepository(db)

    def initiate_transfer(self, body: CarTransferInitiate, user_id: int) -> CarTransferOutgoingResponse:
        car = self.repo.get_car_by_uuid(body.car_uuid, user_id)
        if not car:
            raise HTTPException(404, "Car not found or does not belong to you")
        receiver = self.repo.get_receiver_by_email(body.receiver_email)
        if not receiver:
            raise HTTPException(404, "No user found with that email")
        if receiver.user_id == user_id:
            raise HTTPException(400, "You cannot transfer a car to yourself")
        existing = self.repo.get_pending_by_car(body.car_uuid)
        if existing:
            raise HTTPException(400, "A pending transfer already exists for this car")
        transfer = CarTransfer(
            transfer_uuid=uuid.uuid4(),
            car_uuid=body.car_uuid,
            sender_user_id=user_id,
            receiver_user_id=receiver.user_id,
            status="pending",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48)
        )
        created = self.repo.create(transfer)
        return CarTransferOutgoingResponse(
            transfer_uuid=created.transfer_uuid,
            receiver_email=receiver.email,
            receiver_first_name=receiver.first_name,
            receiver_last_name=receiver.last_name,
            status=created.status,
            created_at=created.created_at,
            expires_at=created.expires_at,
            car_name=car.name,
            car_make=car.make,
            car_model=car.model,
            car_year=car.year
        )

    def get_incoming(self, user_id: int) -> list[CarTransferIncomingResponse]:
        transfers = self.repo.get_incoming(user_id)
        return [
            CarTransferIncomingResponse(
                transfer_uuid=t.transfer_uuid,
                sender_email=t.sender.email,
                sender_first_name=t.sender.first_name,
                sender_last_name=t.sender.last_name,
                status=t.status,
                created_at=t.created_at,
                expires_at=t.expires_at,
                car_name=t.car.name,
                car_make=t.car.make,
                car_model=t.car.model,
                car_year=t.car.year
            )
            for t in transfers
        ]

    def get_outgoing(self, user_id: int) -> list[CarTransferOutgoingResponse]:
        transfers = self.repo.get_outgoing(user_id)
        return [
            CarTransferOutgoingResponse(
                transfer_uuid=t.transfer_uuid,
                receiver_email=t.receiver.email,
                receiver_first_name=t.receiver.first_name,
                receiver_last_name=t.receiver.last_name,
                status=t.status,
                created_at=t.created_at,
                expires_at=t.expires_at,
                car_name=t.car.name,
                car_make=t.car.make,
                car_model=t.car.model,
                car_year=t.car.year
            )
            for t in transfers
        ]

    def accept_transfer(self, transfer_uuid: str, user_id: int) -> dict:
        transfer = self.repo.get_by_uuid_and_receiver(transfer_uuid, user_id)
        if not transfer:
            raise HTTPException(404, "Transfer not found")
        if datetime.now(timezone.utc) > transfer.expires_at:
            self.repo.update_status(transfer, "expired")
            raise HTTPException(400, "Transfer has expired")
        if not transfer.car:
            raise HTTPException(404, "Car no longer exists")
        self.repo.transfer_car_ownership(transfer.car, user_id, transfer)
        return {"message": "Car transfer accepted successfully"}

    def reject_transfer(self, transfer_uuid: str, user_id: int) -> dict:
        transfer = self.repo.get_by_uuid_and_receiver(transfer_uuid, user_id)
        if not transfer:
            raise HTTPException(404, "Transfer not found")
        self.repo.update_status(transfer, "rejected")
        return {"message": "Transfer rejected"}

    def cancel_transfer(self, transfer_uuid: str, user_id: int) -> dict:
        transfer = self.repo.get_by_uuid_and_sender(transfer_uuid, user_id)
        if not transfer:
            raise HTTPException(404, "Transfer not found or already resolved")
        self.repo.update_status(transfer, "cancelled")
        return {"message": "Transfer cancelled"}