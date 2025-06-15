import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select
from app.models.polling_job import PollingJob
from app.services.providers.yahoo import YahooFinanceProvider
from app.services.kafka.producer import publish_price_event
import os
import uuid
DATABASE_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:98310@db:5432/market_data_service")

# Set up async SQLAlchemy session
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit= False)

provider = YahooFinanceProvider()

async def process_job(job: PollingJob):
    while True:
        print(f"⏳ Polling for job {job.id} every {job.interval} seconds...")
        for symbol in job.symbols:
            try:
                result = provider.get_latest_price(symbol)
                result_dict = result.model_dump()
                result_dict["raw_response_id"] = str(uuid.uuid4())
                publish_price_event(result_dict)
                print(f"Published: {result_dict}")
            except Exception as e:
                print(f" Error polling {symbol}: {e}")
        await asyncio.sleep(job.interval)

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PollingJob))
        jobs = result.scalars().all()

        if not jobs:
            print("⚠️ No polling jobs found.")
            return

        await asyncio.gather(*(process_job(job) for job in jobs))

if __name__ == "__main__":
    asyncio.run(main())
