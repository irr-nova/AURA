from backend.contracts import AdaptationFeedback


class AdaptationManager:

    def create_feedback(
        self,
        execution_result,
        portfolio_state,
        risk_decision,
        resulting_position,
    ):

        return AdaptationFeedback(
            execution_outcome=execution_result.status,
            risk_outcome=risk_decision.status,
            resulting_position=resulting_position,
            pnl=portfolio_state.pnl,
            drawdown=portfolio_state.drawdown,
        )