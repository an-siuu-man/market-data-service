from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.models.base import Base

class SymbolAverage(Base):
    __tablename__ = "symbol_averages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    moving_average = Column(Float, nullable=False)
