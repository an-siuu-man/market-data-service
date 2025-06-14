from fastapi import APIRouter, Body, status

from pydantic import BaseModel
from typing import List

router = APIRouter()

class PollRequest(BaseModel):
    symbols: List[str]
    interval: int
    provider: str

class PollResponse(BaseModel):
    job_id: str
    status: str
    config: dict

@router.post("/prices/poll", response_model=PollResponse, status_code=status.HTTP_202_ACCEPTED)
async def poll_prices(request: PollRequest = Body(...)):
    # Placeholder implementation
    return PollResponse(
        job_id="example-job-id",
        status="scheduled",
        config={
            "symbols": request.symbols,
            "interval": request.interval,
            "provider": request.provider
        }
    )