from backend.contracts import (
    MarketState,
    PortfolioState,
    AgentDecision,
)


class AutonomousAgent:

    def decide(
        self,
        market: MarketState,
        portfolio: PortfolioState,
    ) -> AgentDecision:
        raise NotImplementedError