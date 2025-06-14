import yfinance as yf
from app.schemas.price import PriceResponse
from app.services.providers.base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    def get_latest_price(self, symbol: str) -> PriceResponse:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m")

        if hist.empty:
            raise ValueError(f"No data available for symbol '{symbol}'")

        latest_row = hist.iloc[-1]

        return PriceResponse(
            symbol=symbol.upper(),
            price=round(latest_row["Close"], 2),
            timestamp=hist.index[-1].tz_convert("UTC").isoformat().replace('+00:00', 'Z'),  
            provider="yahoo_finance"
        )
