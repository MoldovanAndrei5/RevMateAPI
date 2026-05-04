from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.car_transfer_schema import CarTransferInitiate, CarTransferIncomingResponse, CarTransferOutgoingResponse
from services.transfer_service import TransferService
from utils.auth import get_current_user

router = APIRouter(tags=["Transfers"], dependencies=[Depends(get_current_user)])

def get_transfer_service(db: Session = Depends(get_db)) -> TransferService:
    return TransferService(db)

@router.post("/initiate", response_model=CarTransferOutgoingResponse)
def initiate_transfer(body: CarTransferInitiate, user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.initiate_transfer(body, user_id)

@router.get("/incoming", response_model=list[CarTransferIncomingResponse])
def get_incoming_transfers(user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.get_incoming(user_id)

@router.get("/outgoing", response_model=list[CarTransferOutgoingResponse])
def get_outgoing_transfers(user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.get_outgoing(user_id)

@router.post("/accept/{transfer_uuid}")
def accept_transfer(transfer_uuid: str, user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.accept_transfer(transfer_uuid, user_id)

@router.post("/reject/{transfer_uuid}")
def reject_transfer(transfer_uuid: str, user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.reject_transfer(transfer_uuid, user_id)

@router.delete("/cancel/{transfer_uuid}")
def cancel_transfer(transfer_uuid: str, user_id: int = Depends(get_current_user), service: TransferService = Depends(get_transfer_service)):
    return service.cancel_transfer(transfer_uuid, user_id)