from fastapi import APIRouter
from .prices import router as prices_router



# initializing API router and including the prices and poll router
router = APIRouter()
router.include_router(prices_router, prefix="/prices", tags=["Prices"])
router.include_router(prices_router, prefix="/poll", tags=["Poll"])