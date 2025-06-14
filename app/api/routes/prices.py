from fastapi import APIRouter, Query, HTTPException, Body, status
from typing import List
from app.services.providers.yahoo import YahooFinanceProvider
from app.schemas.price import PriceResponse, PollRequest, PollResponse

router = APIRouter()
yahoo_provider = YahooFinanceProvider()

@router.post("/prices/poll", response_model=PollResponse, status_code=status.HTTP_202_ACCEPTED)
async def poll_prices(request: PollRequest = Body(...)) -> PollResponse:
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

@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(symbol: str = Query(...), provider: str = Query("yahoo")) -> PriceResponse:
    if provider != "yahoo":
        raise HTTPException(status_code=400, detail="Only 'yahoo' provider is supported for now.")
    try:
        return yahoo_provider.get_latest_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))