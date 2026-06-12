from uuid import UUID
from fastapi import APIRouter, Depends
from dependencies.di import get_transfer_service
from schemas.car_transfer_schema import CarTransferInitiate, CarTransferIncomingResponse, CarTransferOutgoingResponse
from schemas.response_schema import MessageResponse
from services.interfaces.i_transfer_service import ITransferService
from utils.auth import get_current_user

router = APIRouter(tags=["Transfers"], dependencies=[Depends(get_current_user)])

@router.post("/initiate", response_model=CarTransferOutgoingResponse)
def initiate_transfer(body: CarTransferInitiate, user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.initiate_transfer(user_id, body)

@router.get("/incoming", response_model=list[CarTransferIncomingResponse])
def get_incoming_transfers(user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.get_incoming(user_id)

@router.get("/outgoing", response_model=list[CarTransferOutgoingResponse])
def get_outgoing_transfers(user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.get_outgoing(user_id)

@router.post("/accept/{transfer_uuid}", response_model=MessageResponse)
def accept_transfer(transfer_uuid: UUID, user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.accept_transfer(transfer_uuid, user_id)

@router.post("/reject/{transfer_uuid}", response_model=MessageResponse)
def reject_transfer(transfer_uuid: UUID, user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.reject_transfer(transfer_uuid, user_id)

@router.delete("/cancel/{transfer_uuid}", response_model=MessageResponse)
def cancel_transfer(transfer_uuid: UUID, user_id: int = Depends(get_current_user), transfer_service: ITransferService = Depends(get_transfer_service)):
    return transfer_service.cancel_transfer(transfer_uuid, user_id)