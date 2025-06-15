import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models.polling_job import PollingJob
from app.models.price_point import PricePoint
from app.services.providers.yahoo import YahooFinanceProvider
from app.services.kafka.producer import publish_price_event
from datetime import datetime
import os
import uuid
DATABASE_URL = os.getenv("DB_URL", "postgresql://postgres:98310@db:5432/market_data_service")

# Set up async SQLAlchemy session
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

provider = YahooFinanceProvider()

async def process_job(job: PollingJob, session: AsyncSession):
    while True:
        print(f"Polling for job {job.id} every {job.interval} seconds...")
        for symbol in job.symbols:
            try:
                result = provider.get_latest_price(str(symbol))
                result_dict = result.model_dump()
                result_dict["raw_response_id"] = str(uuid.uuid4())
                print("BLAH BOLAH BLHAH")
                price_point = PricePoint(
                    symbol=result.symbol,
                    price=result.price,
                    timestamp=datetime.fromisoformat(result.timestamp),
                    provider=result.provider
                )
                session.add(price_point)
                await session.commit()

                publish_price_event(result_dict)
                print(f"Published: {result_dict}")
            except Exception as e:
                print(f" Error polling {symbol}: {e}")
        await asyncio.sleep(float(job.interval))

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PollingJob))
        jobs = result.scalars().all()

        if not jobs:
            print("⚠️ No polling jobs found.")
            return

        await asyncio.gather(*(process_job(job, session) for job in jobs))

if __name__ == "__main__":
    asyncio.run(main())
