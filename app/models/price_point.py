from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.models.base import Base

class PricePoint(Base):
    __tablename__ = "price_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    provider = Column(String, nullable=False)
    raw_response_id = Column(UUID(as_uuid=True), ForeignKey("raw_market_data.id"))
