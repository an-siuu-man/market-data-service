from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from uuid import uuid4
from datetime import datetime, timezone
from app.models.base import Base

class PollingJob(Base):
    __tablename__ = "polling_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbols = Column(ARRAY(String), nullable=False)
    interval = Column(Integer, nullable=False)
    provider = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    status = Column(String, default="accepted")
