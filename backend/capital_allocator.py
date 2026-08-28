from backend.contracts import MarketState, PortfolioState


class CapitalAllocator:
    """Calculates a proposed position size for the autonomous agent.

    This component proposes a quantity based on portfolio allocation.
    Final risk approval is handled by the Risk Engine.
    """

    def calculate_quantity(
        self,
        market: MarketState,
        portfolio: PortfolioState,
        allocation_fraction: float,
    ) -> float:
        if not 0.0 <= allocation_fraction <= 1.0:
            raise ValueError("allocation_fraction must be between 0 and 1")

        if market.price <= 0:
            return 0.0

        if portfolio.total_value <= 0:
            return 0.0

        if portfolio.available_cash <= 0:
            return 0.0

        desired_amount = portfolio.total_value * allocation_fraction

        # The allocator must not propose a BUY larger than available cash.
        allocation_amount = min(desired_amount, portfolio.available_cash)

        quantity = allocation_amount / market.price

        # Use whole shares for the simulated market.
        return float(int(quantity))