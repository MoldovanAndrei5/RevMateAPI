import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_uuid = Column(UUID(as_uuid=True), ForeignKey("maintenance_tasks.task_uuid", ondelete="CASCADE"), nullable=False)
    file_key = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) 
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    task = relationship("MaintenanceTask", back_populates="invoices")