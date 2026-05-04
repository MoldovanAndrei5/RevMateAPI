from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone, timedelta
import uuid

from database import get_db
from models.car_transfer import CarTransfer
from models.car import Car
from models.user import User
from schemas.car_transfer_schema import CarTransferInitiate, CarTransferIncomingResponse, CarTransferOutgoingResponse
from utils.auth import get_current_user

router = APIRouter(tags=["Transfers"], dependencies=[Depends(get_current_user)])


@router.post("/initiate", response_model=CarTransferOutgoingResponse)
def initiate_transfer(
    body: CarTransferInitiate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.car_uuid == body.car_uuid,
        Car.user_id == user_id
    ).first()
    if not car:
        raise HTTPException(404, "Car not found or does not belong to you")

    receiver = db.query(User).filter(User.email == body.receiver_email).first()
    if not receiver:
        raise HTTPException(404, "No user found with that email")

    if receiver.user_id == user_id:
        raise HTTPException(400, "You cannot transfer a car to yourself")

    existing = db.query(CarTransfer).filter(
        CarTransfer.car_uuid == body.car_uuid,
        CarTransfer.status == "pending"
    ).first()
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
    db.add(transfer)
    db.commit()
    db.refresh(transfer)

    return CarTransferOutgoingResponse(
        transfer_uuid=transfer.transfer_uuid,
        receiver_email=receiver.email,
        receiver_first_name=receiver.first_name,
        receiver_last_name=receiver.last_name,
        status=transfer.status,
        created_at=transfer.created_at,
        expires_at=transfer.expires_at,
        car_name=car.name,
        car_make=car.make,
        car_model=car.model,
        car_year=car.year
    )


@router.get("/incoming", response_model=list[CarTransferIncomingResponse])
def get_incoming_transfers(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    transfers = db.query(CarTransfer).options(
        joinedload(CarTransfer.sender),
        joinedload(CarTransfer.car)
    ).filter(
        CarTransfer.receiver_user_id == user_id,
        CarTransfer.status == "pending"
    ).all()

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


@router.get("/outgoing", response_model=list[CarTransferOutgoingResponse])
def get_outgoing_transfers(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    transfers = db.query(CarTransfer).options(
        joinedload(CarTransfer.receiver),
        joinedload(CarTransfer.car)
    ).filter(
        CarTransfer.sender_user_id == user_id,
        CarTransfer.status == "pending"
    ).all()

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


@router.post("/accept/{transfer_uuid}")
def accept_transfer(
    transfer_uuid: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    transfer = db.query(CarTransfer).options(
        joinedload(CarTransfer.car)
    ).filter(
        CarTransfer.transfer_uuid == transfer_uuid,
        CarTransfer.receiver_user_id == user_id,
        CarTransfer.status == "pending"
    ).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")

    if datetime.now(timezone.utc) > transfer.expires_at:
        transfer.status = "expired"
        db.commit()
        raise HTTPException(400, "Transfer has expired")

    car = db.query(Car).filter(Car.car_uuid == transfer.car_uuid).first()
    if not car:
        raise HTTPException(404, "Car no longer exists")

    car.user_id = user_id
    transfer.status = "accepted"
    db.commit()

    return {"message": "Car transfer accepted successfully"}


@router.post("/reject/{transfer_uuid}")
def reject_transfer(
    transfer_uuid: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    transfer = db.query(CarTransfer).filter(
        CarTransfer.transfer_uuid == transfer_uuid,
        CarTransfer.receiver_user_id == user_id,
        CarTransfer.status == "pending"
    ).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")

    transfer.status = "rejected"
    db.commit()

    return {"message": "Transfer rejected"}


@router.delete("/cancel/{transfer_uuid}")
def cancel_transfer(
    transfer_uuid: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    transfer = db.query(CarTransfer).filter(
        CarTransfer.transfer_uuid == transfer_uuid,
        CarTransfer.sender_user_id == user_id,
        CarTransfer.status == "pending"
    ).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found or already resolved")

    transfer.status = "cancelled"
    db.commit()

    return {"message": "Transfer cancelled"}