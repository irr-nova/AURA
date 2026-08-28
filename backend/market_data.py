from backend.contracts import MarketState


class MarketDataProvider:
    """
    Provides market data to the rest of AURA.

    The simulator is currently the data source.
    A real market-data API can be connected later without
    changing the Agent or Risk modules.
    """

    def __init__(self, simulator):
        self.simulator = simulator

    def get_market_state(self, asset: str) -> MarketState:
        return self.simulator.get_market_state(asset)

    def get_all_market_states(self) -> list[MarketState]:
        return self.simulator.get_all_market_states()