from backend.contracts import (
    AdaptationFeedback,
    ExecutionResult,
    PortfolioState,
    RiskDecision,
)


class AdaptationManager:
    """Builds feedback for the Agent after a trading cycle."""

    def create_feedback(
        self,
        execution_result: ExecutionResult,
        portfolio_state: PortfolioState,
        risk_decision: RiskDecision,
        resulting_position: float,
    ) -> AdaptationFeedback:
        """Create AdaptationFeedback from execution, risk, and portfolio outcomes."""

        if resulting_position < 0:
            raise ValueError("resulting_position cannot be negative")

        return AdaptationFeedback(
            execution_outcome=execution_result.status,
            requested_quantity=execution_result.requested_quantity,
            executed_quantity=execution_result.executed_quantity,
            requested_price=execution_result.requested_price,
            executed_price=execution_result.executed_price,
            transaction_cost=execution_result.transaction_cost,
            slippage=execution_result.slippage,
            resulting_portfolio_value=portfolio_state.total_value,
            pnl=portfolio_state.pnl,
            drawdown=portfolio_state.drawdown,
            current_exposure=portfolio_state.current_exposure,
            resulting_position=resulting_position,
            risk_outcome=risk_decision.status,
            timestamp=execution_result.timestamp,
        )