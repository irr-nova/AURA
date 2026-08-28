from datetime import datetime, timezone

import pytest

from backend.adaptation import AdaptationManager
from backend.contracts import (
    ExecutionResult,
    PortfolioState,
    RiskDecision,
)


def make_execution_result(
    status="FILLED",
    requested_quantity=10.0,
    executed_quantity=10.0,
):
    return ExecutionResult(
        status=status,
        asset="AAPL",
        action="BUY",
        requested_quantity=requested_quantity,
        executed_quantity=executed_quantity,
        requested_price=100.0,
        executed_price=100.05,
        transaction_cost=1.0005,
        slippage=0.05,
        timestamp=datetime.now(timezone.utc),
        reason="Order executed successfully",
    )


def make_portfolio_state():
    return PortfolioState(
        available_cash=8989.4995,
        positions={"AAPL": 10.0},
        total_value=9989.9995,
        current_exposure=0.1001,
        pnl=-10.0005,
        drawdown=0.001,
        timestamp=datetime.now(timezone.utc),
    )


def make_risk_decision(status="APPROVE"):
    return RiskDecision(
        status=status,
        approved_quantity=10.0,
        approved_amount=1000.0,
        risk_score=0.1,
        risk_factors=[],
        constraints_triggered=[],
        timestamp=datetime.now(timezone.utc),
    )


def test_create_feedback_from_execution_risk_and_portfolio():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision(),
        resulting_position=10.0,
    )

    assert feedback.execution_outcome == "FILLED"
    assert feedback.requested_quantity == 10.0
    assert feedback.executed_quantity == 10.0
    assert feedback.requested_price == 100.0
    assert feedback.executed_price == 100.05
    assert feedback.transaction_cost == 1.0005
    assert feedback.slippage == 0.05
    assert feedback.resulting_portfolio_value == 9989.9995
    assert feedback.pnl == -10.0005
    assert feedback.drawdown == 0.001
    assert feedback.current_exposure == 0.1001
    assert feedback.resulting_position == 10.0
    assert feedback.risk_outcome == "APPROVE"


def test_partial_execution_is_reported():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(
            status="PARTIAL",
            requested_quantity=10.0,
            executed_quantity=5.0,
        ),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision("MODIFY"),
        resulting_position=5.0,
    )

    assert feedback.execution_outcome == "PARTIAL"
    assert feedback.requested_quantity == 10.0
    assert feedback.executed_quantity == 5.0
    assert feedback.resulting_position == 5.0
    assert feedback.risk_outcome == "MODIFY"


def test_rejected_execution_is_reported():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(status="REJECTED"),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision("REJECT"),
        resulting_position=0.0,
    )

    assert feedback.execution_outcome == "REJECTED"
    assert feedback.risk_outcome == "REJECT"
    assert feedback.resulting_position == 0.0


def test_failed_execution_is_reported():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(status="FAILED"),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision("APPROVE"),
        resulting_position=10.0,
    )

    assert feedback.execution_outcome == "FAILED"


def test_negative_resulting_position_is_rejected():
    manager = AdaptationManager()

    with pytest.raises(ValueError, match="resulting_position"):
        manager.create_feedback(
            execution_result=make_execution_result(),
            portfolio_state=make_portfolio_state(),
            risk_decision=make_risk_decision(),
            resulting_position=-1.0,
        )


def test_feedback_timestamp_is_utc():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision(),
        resulting_position=10.0,
    )

    assert feedback.timestamp.tzinfo is not None
    assert feedback.timestamp.utcoffset() == timezone.utc.utcoffset(
        feedback.timestamp
    )


def test_feedback_is_immutable():
    manager = AdaptationManager()

    feedback = manager.create_feedback(
        execution_result=make_execution_result(),
        portfolio_state=make_portfolio_state(),
        risk_decision=make_risk_decision(),
        resulting_position=10.0,
    )

    with pytest.raises(AttributeError):
        feedback.pnl = 100.0