from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.models.base import Base

class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String, nullable=False)
    data = Column(JSON, nullable=False)

