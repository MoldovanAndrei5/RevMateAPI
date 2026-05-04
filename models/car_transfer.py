import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class CarTransfer(Base):
    __tablename__ = "car_transfers" 

    transfer_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_uuid = Column(UUID(as_uuid=True), ForeignKey("cars.car_uuid", ondelete="CASCADE"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(hours=48), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', 'cancelled', 'expired')",
            name="valid_transfer_status"
        ),
    )

    car = relationship("Car")
    sender = relationship("User", foreign_keys=[sender_user_id])
    receiver = relationship("User", foreign_keys=[receiver_user_id])