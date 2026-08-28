from datetime import datetime, timezone

from .contracts import (
    AgentDecision,
    MarketState,
    PortfolioState,
    RiskConstraints,
    RiskDecision,
)
from .validation import (
    validate_agent_decision,
    validate_market_state,
    validate_portfolio_state,
)


class RiskEngine:
    """
    Evaluates AgentDecision proposals against portfolio and market risk
    constraints.

    The Risk Engine does not execute trades. It only approves, modifies,
    or rejects proposed actions.
    """

    def __init__(self, constraints: RiskConstraints | None = None):
        self.constraints = constraints or RiskConstraints()

    def evaluate(
        self,
        decision: AgentDecision,
        market: MarketState,
        portfolio: PortfolioState,
    ) -> RiskDecision:
        """
        Evaluate an agent decision and return a RiskDecision.
        """

        risk_factors: list[str] = []
        constraints_triggered: list[str] = []

        # ---------------------------------------------------------
        # 1. Validate incoming objects
        # ---------------------------------------------------------

        decision_errors = validate_agent_decision(decision)
        market_errors = validate_market_state(market)
        portfolio_errors = validate_portfolio_state(portfolio)

        validation_errors = (
            decision_errors + market_errors + portfolio_errors
        )

        if validation_errors:
            return self._reject(
                risk_score=1.0,
                risk_factors=validation_errors,
                constraints_triggered=["INPUT_VALIDATION"],
            )

        # ---------------------------------------------------------
        # 2. HOLD requires no trade
        # ---------------------------------------------------------

        if decision.action == "HOLD":
            return RiskDecision(
                status="APPROVE",
                approved_quantity=0.0,
                approved_amount=0.0,
                risk_score=0.0,
                risk_factors=["No trade requested."],
                constraints_triggered=[],
                timestamp=datetime.now(timezone.utc),
            )

        # ---------------------------------------------------------
        # 3. Asset consistency
        # ---------------------------------------------------------

        if decision.asset != market.asset:
            return self._reject(
                risk_score=1.0,
                risk_factors=[
                    "Agent asset does not match current market asset."
                ],
                constraints_triggered=["ASSET_MISMATCH"],
            )

        # ---------------------------------------------------------
        # 4. Market risk checks
        # ---------------------------------------------------------

        if market.volatility > self.constraints.max_volatility:
            constraints_triggered.append("MAX_VOLATILITY")
            risk_factors.append(
                f"Volatility {market.volatility:.2f} exceeds "
                f"limit {self.constraints.max_volatility:.2f}."
            )

        if market.liquidity < self.constraints.min_liquidity:
            constraints_triggered.append("MIN_LIQUIDITY")
            risk_factors.append(
                f"Liquidity {market.liquidity:.2f} is below "
                f"minimum {self.constraints.min_liquidity:.2f}."
            )

        # ---------------------------------------------------------
        # 5. Drawdown protection
        # ---------------------------------------------------------

        if portfolio.drawdown >= self.constraints.max_drawdown:
            constraints_triggered.append("MAX_DRAWDOWN")
            risk_factors.append(
                f"Portfolio drawdown {portfolio.drawdown:.2f} "
                f"reached/exceeded limit "
                f"{self.constraints.max_drawdown:.2f}."
            )

        # ---------------------------------------------------------
        # 6. REDUCE cannot exceed existing position
        # ---------------------------------------------------------

        current_position = portfolio.positions.get(decision.asset, 0.0)

        if decision.action == "REDUCE":
            if decision.requested_quantity > current_position:
                return self._reject(
                    risk_score=1.0,
                    risk_factors=[
                        "Requested reduction exceeds existing position."
                    ],
                    constraints_triggered=["POSITION_LIMIT"],
                )

        # ---------------------------------------------------------
        # 7. SELL cannot exceed existing position
        # ---------------------------------------------------------

        if decision.action == "SELL":
            if decision.requested_quantity > current_position:
                return self._reject(
                    risk_score=1.0,
                    risk_factors=[
                        "Requested sell quantity exceeds existing position."
                    ],
                    constraints_triggered=["POSITION_LIMIT"],
                )

        # ---------------------------------------------------------
        # 8. Calculate proposed trade value
        # ---------------------------------------------------------

        requested_amount = decision.requested_amount

        # ---------------------------------------------------------
        # 9. BUY cash check
        # ---------------------------------------------------------

        if decision.action == "BUY":
            if requested_amount > portfolio.available_cash:
                constraints_triggered.append("AVAILABLE_CASH")
                risk_factors.append(
                    "Requested purchase exceeds available cash."
                )

        # ---------------------------------------------------------
        # 10. Position allocation limit
        # ---------------------------------------------------------

        max_trade_value = (
            portfolio.total_value
            * self.constraints.max_position_allocation
        )

        if requested_amount > max_trade_value:
            constraints_triggered.append("MAX_POSITION_ALLOCATION")
            risk_factors.append(
                f"Trade amount ₹{requested_amount:.2f} exceeds "
                f"maximum new allocation ₹{max_trade_value:.2f}."
            )

        # ---------------------------------------------------------
        # 11. Calculate resulting exposure
        # ---------------------------------------------------------

        current_asset_value = current_position * market.price

        if decision.action == "BUY":
            resulting_asset_value = (
                current_asset_value + requested_amount
            )
        else:
            resulting_asset_value = max(
                0.0,
                current_asset_value - requested_amount,
            )

        resulting_total_asset_exposure = (
            resulting_asset_value / portfolio.total_value
        )

        # ---------------------------------------------------------
        # 12. Single asset exposure limit
        # ---------------------------------------------------------

        if (
            resulting_total_asset_exposure
            > self.constraints.max_single_asset_exposure
        ):
            constraints_triggered.append("MAX_SINGLE_ASSET_EXPOSURE")
            risk_factors.append(
                f"Resulting asset exposure "
                f"{resulting_total_asset_exposure:.2f} exceeds "
                f"limit "
                f"{self.constraints.max_single_asset_exposure:.2f}."
            )

        # ---------------------------------------------------------
        # 13. Portfolio exposure limit
        # ---------------------------------------------------------

        current_position_value = sum(
            quantity * market.price
            for asset, quantity in portfolio.positions.items()
            if asset == market.asset
        )

        current_exposure = portfolio.current_exposure

        trade_exposure_change = (
            requested_amount / portfolio.total_value
        )

        if decision.action == "BUY":
            resulting_portfolio_exposure = (
                current_exposure + trade_exposure_change
            )
        else:
            resulting_portfolio_exposure = max(
                0.0,
                current_exposure - trade_exposure_change,
            )

        if (
            resulting_portfolio_exposure
            > self.constraints.max_portfolio_exposure
        ):
            constraints_triggered.append("MAX_PORTFOLIO_EXPOSURE")
            risk_factors.append(
                f"Resulting portfolio exposure "
                f"{resulting_portfolio_exposure:.2f} exceeds "
                f"limit "
                f"{self.constraints.max_portfolio_exposure:.2f}."
            )

        # ---------------------------------------------------------
        # 14. Determine risk score
        # ---------------------------------------------------------

        risk_score = self._calculate_risk_score(
            market=market,
            portfolio=portfolio,
            triggered_count=len(constraints_triggered),
        )

        # ---------------------------------------------------------
        # 15. Reject severe violations
        # ---------------------------------------------------------

        severe_constraints = {
            "INPUT_VALIDATION",
            "ASSET_MISMATCH",
            "POSITION_LIMIT",
            "MAX_DRAWDOWN",
        }

        if any(
            constraint in severe_constraints
            for constraint in constraints_triggered
        ):
            return self._reject(
                risk_score=risk_score,
                risk_factors=risk_factors,
                constraints_triggered=constraints_triggered,
            )

        # ---------------------------------------------------------
        # 16. Modify trade if it exceeds adjustable limits
        # ---------------------------------------------------------

        approved_quantity = decision.requested_quantity
        approved_amount = decision.requested_amount

        if constraints_triggered:

            if "AVAILABLE_CASH" in constraints_triggered:
                approved_amount = min(
                    approved_amount,
                    portfolio.available_cash,
                )

            if "MAX_POSITION_ALLOCATION" in constraints_triggered:
                approved_amount = min(
                    approved_amount,
                    max_trade_value,
                )

            if "MAX_SINGLE_ASSET_EXPOSURE" in constraints_triggered:
                maximum_asset_value = (
                    portfolio.total_value
                    * self.constraints.max_single_asset_exposure
                )

                if decision.action == "BUY":
                    allowable_amount = max(
                        0.0,
                        maximum_asset_value - current_asset_value,
                    )
                else:
                    allowable_amount = approved_amount

                approved_amount = min(
                    approved_amount,
                    allowable_amount,
                )

            if "MAX_PORTFOLIO_EXPOSURE" in constraints_triggered:
                maximum_portfolio_value = (
                    portfolio.total_value
                    * self.constraints.max_portfolio_exposure
                )

                if decision.action == "BUY":
                    current_exposed_value = (
                        portfolio.total_value
                        * current_exposure
                    )

                    allowable_amount = max(
                        0.0,
                        maximum_portfolio_value
                        - current_exposed_value,
                    )

                    approved_amount = min(
                        approved_amount,
                        allowable_amount,
                    )

            approved_quantity = (
                approved_amount / market.price
                if market.price > 0
                else 0.0
            )

            if approved_quantity <= 0:
                return self._reject(
                    risk_score=risk_score,
                    risk_factors=risk_factors,
                    constraints_triggered=constraints_triggered,
                )

            return RiskDecision(
                status="MODIFY",
                approved_quantity=approved_quantity,
                approved_amount=approved_amount,
                risk_score=risk_score,
                risk_factors=risk_factors,
                constraints_triggered=constraints_triggered,
                timestamp=datetime.now(timezone.utc),
            )

        # ---------------------------------------------------------
        # 17. Everything passed
        # ---------------------------------------------------------

        return RiskDecision(
            status="APPROVE",
            approved_quantity=approved_quantity,
            approved_amount=approved_amount,
            risk_score=risk_score,
            risk_factors=["All configured risk checks passed."],
            constraints_triggered=[],
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _reject(
        risk_score: float,
        risk_factors: list[str],
        constraints_triggered: list[str],
    ) -> RiskDecision:
        """Create a rejected RiskDecision."""

        return RiskDecision(
            status="REJECT",
            approved_quantity=0.0,
            approved_amount=0.0,
            risk_score=min(1.0, max(0.0, risk_score)),
            risk_factors=risk_factors,
            constraints_triggered=constraints_triggered,
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _calculate_risk_score(
        market: MarketState,
        portfolio: PortfolioState,
        triggered_count: int,
    ) -> float:
        """
        Produce a simple normalized risk score.

        Higher volatility, lower liquidity, higher drawdown, and triggered
        constraints increase the score.
        """

        volatility_component = min(1.0, market.volatility)

        liquidity_component = 1.0 - market.liquidity

        drawdown_component = min(1.0, portfolio.drawdown)

        constraint_component = min(
            1.0,
            triggered_count * 0.15,
        )

        score = (
            volatility_component * 0.35
            + liquidity_component * 0.25
            + drawdown_component * 0.25
            + constraint_component * 0.15
        )

        return min(1.0, max(0.0, score))