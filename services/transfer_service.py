from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from fastapi import HTTPException
from models.car_transfer import CarTransfer
from repositories.interfaces.i_user_repository import IUserRepository
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_transfer_repository import ITransferRepository
from schemas.car_transfer_schema import CarTransferInitiate, CarTransferIncomingResponse, CarTransferOutgoingResponse
from services.interfaces.i_transfer_service import ITransferService
from utils.logger import get_logger


logger = get_logger(__name__)

class TransferService(ITransferService):
    def __init__(self, repo: ITransferRepository, car_repo: ICarRepository, user_repo: IUserRepository):
        self.repo = repo
        self.car_repo = car_repo
        self.user_repo = user_repo
        
    def _validate_incoming_owner(self, transfer_uuid: UUID, user_id: int) -> CarTransfer:
        transfer = self.repo.get_pending_by_uuid(transfer_uuid)
        if not transfer:
            logger.warning(f"Transfer {transfer_uuid} not found")
            raise HTTPException(status_code=404, detail="Transfer not found")
        if transfer.receiver_user_id != user_id:
            logger.warning(f"Transfer {transfer_uuid} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Transfer does not belong to user")
        return transfer
    
    def _validate_outgoing_owner(self, transfer_uuid: UUID, user_id: int) -> CarTransfer:
        transfer = self.repo.get_pending_by_uuid(transfer_uuid)
        if not transfer:
            logger.warning(f"Transfer {transfer_uuid} not found")
            raise HTTPException(status_code=404, detail="Transfer not found")
        if transfer.sender_user_id != user_id:
            logger.warning(f"Transfer {transfer_uuid} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Transfer does not belong to user")
        return transfer

    def initiate_transfer(self, body: CarTransferInitiate, user_id: int) -> CarTransferOutgoingResponse:
        logger.info(f"Initiating transfer for car {body.car_uuid} by user {user_id}")
        car = self.car_repo.get_by_uuid(body.car_uuid)
        if not car:
            logger.warning(f"Car {body.car_uuid} not found")
            raise HTTPException(status_code=404, detail="Car not found")
        if car.user_id != user_id:
            logger.warning(f"Car {body.car_uuid} does not belong to user {user_id}")
            raise HTTPException(status_code=403, detail="Car does not belong to user")
        receiver = self.user_repo.get_by_email(body.receiver_email)
        if not receiver:
            logger.warning(f"No user {body.receiver_email} found")
            raise HTTPException(status_code=404, detail="No user found with that email")
        if receiver.user_id == user_id:
            logger.warning(f"Can't transfer your car {body.car_uuid} to yourself")
            raise HTTPException(status_code=400, detail="You cannot transfer your car to yourself")
        existing = self.repo.get_pending_by_car(body.car_uuid)
        if existing:
            logger.warning(f"There is already a transfer {existing.transfer_uuid} for car {body.car_uuid}")
            raise HTTPException(400, "A pending transfer already exists for this car")
        transfer = CarTransfer(
            transfer_uuid=uuid4(),
            car_uuid=body.car_uuid,
            sender_user_id=user_id,
            receiver_user_id=receiver.user_id,
            status="pending",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48)
        )
        created = self.repo.create(transfer)
        logger.info(f"Created transfer {transfer.transfer_uuid}")
        return CarTransferOutgoingResponse(
            transfer_uuid=created.transfer_uuid,
            car_uuid=body.car_uuid,
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
        logger.info(f"Getting incoming transfers for user {user_id}")
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
        logger.info(f"Getting outgoing transfers for user {user_id}")
        transfers = self.repo.get_outgoing(user_id)
        return [
            CarTransferOutgoingResponse(
                transfer_uuid=t.transfer_uuid,
                car_uuid=t.car_uuid,
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

    def accept_transfer(self, transfer_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Accepting transfer {transfer_uuid} for user {user_id}")
        transfer = self._validate_incoming_owner(transfer_uuid, user_id)
        if datetime.now(timezone.utc) > transfer.expires_at:
            logger.warning(f"Transfer {transfer_uuid} expired")
            self.repo.update_status(transfer, "expired")
            raise HTTPException(400, "Transfer has expired")
        if not transfer.car:
            logger.warning(f"Car {transfer.car_uuid} no longer exists")
            raise HTTPException(404, "Car no longer exists")
        self.repo.transfer_car_ownership(transfer.car, user_id, transfer)
        logger.info(f"Accepted transfer {transfer_uuid}")
        return {"message": "Transfer accepted"}

    def reject_transfer(self, transfer_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Rejecting transfer {transfer_uuid} for user {user_id}")
        transfer = self._validate_incoming_owner(transfer_uuid, user_id)
        self.repo.update_status(transfer, "rejected")
        logger.info(f"Transfer {transfer_uuid} rejected")
        return {"message": "Transfer rejected"}

    def cancel_transfer(self, transfer_uuid: UUID, user_id: int) -> dict:
        logger.info(f"Cancelling transfer {transfer_uuid} for user {user_id}")
        transfer = self._validate_outgoing_owner(transfer_uuid, user_id)
        self.repo.update_status(transfer, "cancelled")
        logger.info(f"Transfer {transfer_uuid} cancelled")
        return {"message": "Transfer cancelled"}
