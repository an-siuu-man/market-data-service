# This script polls for jobs in the database and processes them asynchronously.
# It fetches the latest prices for each symbol, stores them, and publishes events to Kafka.
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.models.polling_job import PollingJob
from app.models.price_point import PricePoint
from app.services.providers.yahoo import YahooFinanceProvider
from app.services.kafka.producer import publish_price_event
from datetime import datetime
import os
import uuid
import asyncpg

def get_asyncpg_url():
    """Get the asyncpg-compatible database URL from environment or default."""
    url = os.getenv("DB_URL", "postgresql://postgres:98310@db:5432/market_data_service")
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = get_asyncpg_url()

# Set up async SQLAlchemy session
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

provider = YahooFinanceProvider()

async def process_job(job: PollingJob, session: AsyncSession):
    """
    Polls for the given job at the specified interval, fetches latest prices,
    stores them in the database, and publishes events to Kafka.
    """
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
                    timestamp=datetime.fromisoformat(result.timestamp.replace("Z", "+00:00")).replace(tzinfo=None),
                    provider=result.provider
                )
                session.add(price_point)
                await session.commit()

                publish_price_event(result_dict)
                print(f"Published: {result_dict}")
            except Exception as e:
                print(f" Error polling {symbol}: {e}")
                await session.rollback()
        await asyncio.sleep(float(job.interval))

async def listen_for_new_jobs():
    pg_url = os.getenv("DB_URL", "postgresql://postgres:98310@db:5432/market_data_service")
    pg_url = pg_url.replace("+asyncpg", "")  # asyncpg.connect expects no driver
    conn = await asyncpg.connect(pg_url)
    await conn.add_listener('new_polling_job', on_new_polling_job)
    print("Listening for new polling jobs...")
    while True:
        await asyncio.sleep(3600)  # keep alive

async def on_new_polling_job(_conn, _pid, _channel, payload):
    print(f"Received NOTIFY for new polling job: {payload}")
    # Start processing the new job
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PollingJob).where(PollingJob.id == payload))
        job = result.scalar_one_or_none()
        if job:
            asyncio.create_task(process_job(job, session))
        else:
            print(f"Polling job {payload} not found.")

async def main():
    print("[poller] Starting up and initializing...")
    # Start the NOTIFY listener
    listener_task = asyncio.create_task(listen_for_new_jobs())
    # Keep checking for polling jobs until at least one is found
    jobs = []
    async with AsyncSessionLocal() as session:
        while not jobs:
            result = await session.execute(select(PollingJob))
            jobs = result.scalars().all()
            if not jobs:
                print("[poller] No polling jobs found. Retrying in 3 seconds...")
                await asyncio.sleep(3)
        for job in jobs:
            asyncio.create_task(process_job(job, session))
    await listener_task

if __name__ == "__main__":
    asyncio.run(main())
