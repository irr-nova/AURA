import random
from datetime import datetime, timezone

from backend.contracts import MarketState


class MarketSimulator:
    """
    Simulates a continuously changing financial market.

    This is used for the AURA prototype instead of a live brokerage/
    market-data connection.
    """

    def __init__(self):
        self.assets = {
            "AAPL": {
                "price": 215.40,
                "volume": 1_250_000,
                "liquidity": 0.87,
                "volatility": 0.24,
                "sentiment": 0.65,
                "news_signal": 0.72,
            },
            "TSLA": {
                "price": 182.40,
                "volume": 980_000,
                "liquidity": 0.78,
                "volatility": 0.38,
                "sentiment": 0.20,
                "news_signal": 0.15,
            },
            "NVDA": {
                "price": 141.20,
                "volume": 1_800_000,
                "liquidity": 0.91,
                "volatility": 0.29,
                "sentiment": 0.72,
                "news_signal": 0.68,
            },
        }

    def _calculate_regime(self, volatility, sentiment):
        """Determine the current market regime."""

        if volatility >= 0.40:
            return "HIGH_VOLATILITY"

        if sentiment >= 0.30:
            return "BULL"

        if sentiment <= -0.30:
            return "BEAR"

        return "SIDEWAYS"

    def _update_asset(self, asset):
        """Apply a small random market movement to an asset."""

        data = self.assets[asset]

        # Price movement influenced by sentiment and random market noise.
        price_change = random.gauss(
            data["sentiment"] * 0.001,
            data["volatility"] * 0.005
        )

        data["price"] *= (1 + price_change)

        # Keep price realistic for the simulation.
        data["price"] = max(data["price"], 1.0)

        # Volume changes slightly every tick.
        volume_change = random.uniform(0.95, 1.05)
        data["volume"] *= volume_change

        # Liquidity changes gradually.
        liquidity_change = random.uniform(-0.02, 0.02)
        data["liquidity"] += liquidity_change
        data["liquidity"] = max(0.05, min(data["liquidity"], 1.0))

        # Volatility changes gradually.
        volatility_change = random.uniform(-0.02, 0.02)
        data["volatility"] += volatility_change
        data["volatility"] = max(0.05, min(data["volatility"], 0.80))

        # Sentiment changes gradually.
        sentiment_change = random.uniform(-0.08, 0.08)
        data["sentiment"] += sentiment_change
        data["sentiment"] = max(-1.0, min(data["sentiment"], 1.0))

        # News signal follows sentiment with some randomness.
        data["news_signal"] = (
            data["sentiment"] + random.uniform(-0.15, 0.15)
        )
        data["news_signal"] = max(
            -1.0,
            min(data["news_signal"], 1.0)
        )

    def get_market_state(self, asset):
        """
        Generate the latest MarketState for one asset.
        """

        if asset not in self.assets:
            raise ValueError(f"Unknown asset: {asset}")

        self._update_asset(asset)

        data = self.assets[asset]

        return MarketState(
            asset=asset,
            price=round(data["price"], 2),
            volume=round(data["volume"], 2),
            liquidity=round(data["liquidity"], 4),
            volatility=round(data["volatility"], 4),
            sentiment=round(data["sentiment"], 4),
            news_signal=round(data["news_signal"], 4),
            market_regime=self._calculate_regime(
                data["volatility"],
                data["sentiment"]
            ),
            timestamp=datetime.now(timezone.utc),
            data_age_seconds=0.0,
        )

    def get_all_market_states(self):
        """
        Generate the latest MarketState for every simulated asset.
        """

        return [
            self.get_market_state(asset)
            for asset in self.assets
        ]