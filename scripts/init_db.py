# This script initializes the database and creates tables/triggers if needed.
from app.models.base import Base
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
import time

DATABASE_URL = "postgresql://postgres:98310@db:5432/market_data_service"

def wait_for_db(url, retries=10, delay=3):
    """
    Wait for the database to become available before proceeding.
    """
    for i in range(retries):
        try:
            test_engine = create_engine(url)
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except OperationalError as e:
            print(f"Database not ready, retrying in {delay}s... ({i+1}/{retries})")
            time.sleep(delay)
    raise Exception("Database not available after waiting.")

engine = create_engine(DATABASE_URL, echo=True)

def init_models():
    """
    Create missing tables and triggers in the database if they do not exist.
    """
    with engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = inspector.get_table_names()
        needed_tables = set(Base.metadata.tables.keys())
        if not needed_tables.issubset(set(existing_tables)):
            Base.metadata.create_all(conn)
            print("Created missing tables.")
        else:
            print("All tables already exist. Skipping creation.")

        # Only create trigger if polling_job table exists
        if 'polling_job' in existing_tables:
            conn.execute(text('''
            CREATE OR REPLACE FUNCTION notify_new_polling_job() RETURNS trigger AS $$
            BEGIN
                PERFORM pg_notify('new_polling_job', NEW.id::text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            '''))
            conn.execute(text('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'polling_job_notify_trigger'
                ) THEN
                    CREATE TRIGGER polling_job_notify_trigger
                    AFTER INSERT ON polling_job
                    FOR EACH ROW EXECUTE FUNCTION notify_new_polling_job();
                END IF;
            END$$;
            '''))
            print("Polling job NOTIFY trigger ensured.")
        else:
            print("polling_job table does not exist, skipping NOTIFY trigger setup.")

def main():
    wait_for_db(DATABASE_URL)
    init_models()

if __name__ == "__main__":
    main()