from dataclasses import dataclass
from datetime import datetime, timezone
import random


@dataclass
class MarketState:
    asset: str
    price: float
    volume: float
    liquidity: float
    volatility: float
    sentiment: float
    news_signal: float
    market_regime: str
    timestamp: datetime
    data_age_seconds: float = 0.0


class MarketSimulator:
    """
    Simple deterministic market simulator for AURA.

    Supports:
        AAPL
        TSLA
        NVDA

    Every supported asset is handled identically.
    """

    BASE_PRICES = {
        "AAPL": 225.00,
        "TSLA": 181.79,
        "NVDA": 142.95,
    }

    def __init__(self):
        self._prices = dict(self.BASE_PRICES)

    def get_market_state(self, asset: str) -> MarketState:
        """
        Return a simulated MarketState for the requested asset.
        """

        if not isinstance(asset, str):
            raise ValueError("Asset must be a string.")

        asset = asset.strip().upper()

        if asset not in self._prices:
            raise ValueError(
                f"Unsupported asset: {asset}. "
                f"Supported assets: {', '.join(self._prices.keys())}"
            )

        # Small random price movement.
        base_price = self._prices[asset]

        movement = random.uniform(-0.015, 0.015)
        price = base_price * (1.0 + movement)

        # Keep the new price for the next simulation cycle.
        self._prices[asset] = price

        volume = random.uniform(
            1_000_000,
            10_000_000,
        )

        liquidity = random.uniform(
            0.70,
            0.99,
        )

        volatility = random.uniform(
            0.10,
            0.40,
        )

        sentiment = random.uniform(
            -1.0,
            1.0,
        )

        news_signal = random.uniform(
            -1.0,
            1.0,
        )

        # Determine simulated market regime.
        if volatility >= 0.30:
            market_regime = "HIGH_VOLATILITY"
        elif sentiment >= 0.30:
            market_regime = "BULLISH"
        elif sentiment <= -0.30:
            market_regime = "BEARISH"
        else:
            market_regime = "NEUTRAL"

        timestamp = datetime.now(timezone.utc)

        return MarketState(
            asset=asset,
            price=round(price, 2),
            volume=round(volume, 0),
            liquidity=round(liquidity, 4),
            volatility=round(volatility, 4),
            sentiment=round(sentiment, 4),
            news_signal=round(news_signal, 4),
            market_regime=market_regime,
            timestamp=timestamp,
            data_age_seconds=0.0,
        )