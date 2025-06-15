from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:98310@db:5432/market_data_service"
engine = create_async_engine(DATABASE_URL, echo=True)

async def init_models():
    async with engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = await conn.run_sync(inspector.get_table_names)
        needed_tables = set(Base.metadata.tables.keys())
        if not needed_tables.issubset(set(existing_tables)):
            await conn.run_sync(Base.metadata.create_all)
            print("Created missing tables.")
        else:
            print("All tables already exist. Skipping creation.")

async def main():
    await init_models()

if __name__ == "__main__":
    asyncio.run(main())