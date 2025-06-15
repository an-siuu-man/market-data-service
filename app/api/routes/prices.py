from fastapi import APIRouter, Query, HTTPException, Body, status, Depends
from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.services.providers.yahoo import YahooFinanceProvider
from app.schemas.price import PriceResponse, PollRequest, PollResponse

from app.models.polling_job import PollingJob
from app.models.raw_market_data import RawMarketData
from app.models.price_point import PricePoint

router = APIRouter()
yahoo_provider = YahooFinanceProvider()

@router.post("/prices/poll", response_model=PollResponse, status_code=status.HTTP_202_ACCEPTED)
async def poll_prices(
    request: PollRequest = Body(...),
    db: Session = Depends(get_db)
) -> PollResponse:
    job_id = str(uuid4())

    polling_job = PollingJob(
        id=job_id,
        symbols=request.symbols,
        interval=request.interval,
        provider=request.provider,
        created_at=datetime.now(timezone.utc),
        status="accepted"
    )

    db.add(polling_job)
    db.commit()

    return PollResponse(
        job_id=job_id,
        status="accepted",
        config={
            "symbols": request.symbols,
            "interval": request.interval,
            "provider": request.provider
        }
    )


@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    symbol: str = Query(...),
    provider: str = Query("yahoo"),
    db: Session = Depends(get_db)
) -> PriceResponse:
    if provider != "yahoo":
        raise HTTPException(status_code=400, detail="Only 'yahoo' provider is supported for now.")
    
    try:
        # 1. Get price from provider
        price_response = yahoo_provider.get_latest_price(symbol)

        # 2. Store raw response
        raw = RawMarketData(
            id=uuid4(),
            symbol=price_response.symbol,
            timestamp=datetime.fromisoformat(price_response.timestamp.replace("Z", "+00:00")),
            source=provider,
            data=price_response.model_dump()  # optionally store entire response
        )
        db.add(raw)
        db.flush()  # to get raw.id before commit

        # 3. Store processed price
        point = PricePoint(
            id=uuid4(),
            symbol=price_response.symbol,
            timestamp=datetime.fromisoformat(price_response.timestamp.replace("Z", "+00:00")),
            price=price_response.price,
            provider=provider,
            raw_response_id=raw.id
        )
        db.add(point)
        db.commit()

        return price_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
