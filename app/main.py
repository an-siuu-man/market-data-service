from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import api_router
from app.core.scheduler import scheduler
from apscheduler.triggers.interval import IntervalTrigger

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

app = FastAPI(title="Market Data Service", lifespan=lifespan)
app.include_router(api_router)


def debug_job_inspector():
    print("🔍 Current scheduled jobs:")
    for job in scheduler.get_jobs():
        print(f"  - {job.id}: next run at {job.next_run_time}")

scheduler.add_job(debug_job_inspector, IntervalTrigger(seconds=30), id="debug-inspector", replace_existing=True)