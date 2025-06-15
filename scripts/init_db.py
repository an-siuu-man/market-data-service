from app.models.base import Base
from app.models.polling_job import PollingJob
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:98310@db:5432/market_data_service"

engine = create_async_engine(DATABASE_URL, echo=True)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
