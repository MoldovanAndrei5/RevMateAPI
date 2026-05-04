from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base


class Car(Base):
    __tablename__ = "cars"

    car_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100))
    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    vin = Column(String(17), unique=True, index=True)
    mileage = Column(Integer)
    license_plate = Column(String(20))
    image_key = Column(String(500), nullable=True)

    user = relationship("User", back_populates="cars")
    tasks = relationship("MaintenanceTask", back_populates="car", cascade="all, delete-orphan")