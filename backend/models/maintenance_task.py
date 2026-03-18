from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    
    task_uuid = Column(UUID(as_uuid=True), primary_key=True)
    car_uuid = Column(UUID(as_uuid=True), ForeignKey("cars.car_uuid", ondelete="CASCADE"), index=True)
    title = Column(String(150))
    category = Column(String(50))
    mileage = Column(Integer, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    scheduled_date = Column(Integer, nullable=True)
    completed_date = Column(Integer, nullable=True)
    notes = Column(String(1000), nullable=True)
    car = relationship("Car", back_populates="tasks")