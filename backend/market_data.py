from backend.market_simulator import MarketSimulator


class MarketDataProvider:
    """
    Provides market data to the AURA application.

    The provider delegates market-state generation to the
    configured market simulator.
    """

    def __init__(self, simulator=None):
        self.simulator = simulator or MarketSimulator()

    def get_market_state(self, asset: str):
        """
        Get market state for any supported asset.
        """

        if not asset:
            raise ValueError("Asset cannot be empty.")

        asset = str(asset).strip().upper()

        return self.simulator.get_market_state(asset)