from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
import os

# Change the database host to 'db' in the DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:98310@db:5432/market_data_service")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
