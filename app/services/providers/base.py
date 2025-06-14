from abc import ABC, abstractmethod
from typing import Dict


class MarketDataProvider(ABC):
    @abstractmethod
    def get_latest_price(self, symbol: str) -> Dict:
        """Fetch the latest price for a given symbol."""
        pass
