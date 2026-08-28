from datetime import datetime, timezone

from backend.contracts import (
    MarketState,
    PortfolioState,
    AgentDecision,
)
from backend.capital_allocator import CapitalAllocator


class AutonomousAgent:
    """Rule-based autonomous decision engine for the AURA simulator.

    The agent evaluates market conditions together with the current
    portfolio state and proposes an action. Risk approval happens later
    in the Risk Engine.
    """

    MIN_LIQUIDITY = 0.30
    MAX_VOLATILITY = 0.50
    MAX_DATA_AGE_SECONDS = 60.0

    STRONG_BUY_SCORE = 0.60
    BUY_SCORE = 0.25
    REDUCE_SCORE = -0.25
    SELL_SCORE = -0.60

    def __init__(self, allocator: CapitalAllocator | None = None):
        self.allocator = allocator or CapitalAllocator()

    def _opportunity_score(self, market: MarketState) -> float:
        """Calculate a simple explainable opportunity score."""

        sentiment_score = market.sentiment
        news_score = market.news_signal

        liquidity_score = (market.liquidity * 2.0) - 1.0
        volatility_penalty = market.volatility * 1.5

        score = (
            0.35 * sentiment_score
            + 0.30 * news_score
            + 0.20 * liquidity_score
            - 0.15 * volatility_penalty
        )

        return max(-1.0, min(1.0, score))

    def _confidence(self, score: float, market: MarketState) -> float:
        """Convert the opportunity score into a confidence value."""

        confidence = 0.50 + (abs(score) * 0.50)

        if market.data_age_seconds > self.MAX_DATA_AGE_SECONDS:
            confidence *= 0.50

        return max(0.0, min(1.0, confidence))

    def decide(
        self,
        market: MarketState,
        portfolio: PortfolioState,
    ) -> AgentDecision:

        now = datetime.now(timezone.utc)

        # ---------------------------------------------------------
        # 1. Basic validation
        # ---------------------------------------------------------

        if market.price <= 0:
            return AgentDecision(
                action="HOLD",
                asset=market.asset,
                requested_quantity=0.0,
                requested_amount=0.0,
                confidence=0.0,
                expected_return=0.0,
                reason="Invalid market price; holding.",
                timestamp=now,
            )

        # ---------------------------------------------------------
        # 2. Check stale market data
        # ---------------------------------------------------------

        if market.data_age_seconds > self.MAX_DATA_AGE_SECONDS:
            return AgentDecision(
                action="HOLD",
                asset=market.asset,
                requested_quantity=0.0,
                requested_amount=0.0,
                confidence=0.20,
                expected_return=0.0,
                reason="Market data is stale; holding until fresh data arrives.",
                timestamp=now,
            )

        # ---------------------------------------------------------
        # 3. Calculate opportunity
        # ---------------------------------------------------------

        score = self._opportunity_score(market)
        confidence = self._confidence(score, market)

        existing_quantity = portfolio.positions.get(market.asset, 0.0)

        # ---------------------------------------------------------
        # 4. Poor liquidity / excessive volatility
        # ---------------------------------------------------------

        if market.liquidity < self.MIN_LIQUIDITY:
            if existing_quantity > 0:
                return AgentDecision(
                    action="REDUCE",
                    asset=market.asset,
                    requested_quantity=existing_quantity * 0.25,
                    requested_amount=market.price * existing_quantity * 0.25,
                    confidence=confidence,
                    expected_return=score,
                    reason="Liquidity is deteriorating; reducing existing exposure.",
                    timestamp=now,
                )

            return AgentDecision(
                action="HOLD",
                asset=market.asset,
                requested_quantity=0.0,
                requested_amount=0.0,
                confidence=confidence,
                expected_return=score,
                reason="Liquidity is below the acceptable threshold; holding.",
                timestamp=now,
            )

        if market.volatility > self.MAX_VOLATILITY:
            if existing_quantity > 0:
                return AgentDecision(
                    action="REDUCE",
                    asset=market.asset,
                    requested_quantity=existing_quantity * 0.25,
                    requested_amount=market.price * existing_quantity * 0.25,
                    confidence=confidence,
                    expected_return=score,
                    reason="Volatility is elevated; reducing existing exposure.",
                    timestamp=now,
                )

            return AgentDecision(
                action="HOLD",
                asset=market.asset,
                requested_quantity=0.0,
                requested_amount=0.0,
                confidence=confidence,
                expected_return=score,
                reason="Volatility is too high for a new position; holding.",
                timestamp=now,
            )

        # ---------------------------------------------------------
        # 5. Strong negative opportunity
        # ---------------------------------------------------------

        if score <= self.SELL_SCORE and existing_quantity > 0:
            return AgentDecision(
                action="SELL",
                asset=market.asset,
                requested_quantity=existing_quantity,
                requested_amount=market.price * existing_quantity,
                confidence=confidence,
                expected_return=score,
                reason="Market conditions are strongly negative; exiting position.",
                timestamp=now,
            )

        # ---------------------------------------------------------
        # 6. Moderate negative opportunity
        # ---------------------------------------------------------

        if score <= self.REDUCE_SCORE and existing_quantity > 0:
            quantity = existing_quantity * 0.25

            return AgentDecision(
                action="REDUCE",
                asset=market.asset,
                requested_quantity=quantity,
                requested_amount=market.price * quantity,
                confidence=confidence,
                expected_return=score,
                reason="Opportunity has weakened; reducing existing exposure.",
                timestamp=now,
            )

        # ---------------------------------------------------------
        # 7. Strong positive opportunity
        # ---------------------------------------------------------

        if score >= self.BUY_SCORE and portfolio.available_cash > 0:

            if score >= self.STRONG_BUY_SCORE:
                allocation_fraction = 0.20
            else:
                allocation_fraction = 0.10

            quantity = self.allocator.calculate_quantity(
                market,
                portfolio,
                allocation_fraction,
            )

            amount = quantity * market.price

            if quantity > 0:
                return AgentDecision(
                    action="BUY",
                    asset=market.asset,
                    requested_quantity=quantity,
                    requested_amount=amount,
                    confidence=confidence,
                    expected_return=score,
                    reason=(
                        "Positive sentiment, news and liquidity support "
                        "a new position."
                    ),
                    timestamp=now,
                )

        # ---------------------------------------------------------
        # 8. Otherwise hold
        # ---------------------------------------------------------

        return AgentDecision(
            action="HOLD",
            asset=market.asset,
            requested_quantity=0.0,
            requested_amount=0.0,
            confidence=confidence,
            expected_return=score,
            reason="Signals are not strong enough for a trade; holding.",
            timestamp=now,
        )