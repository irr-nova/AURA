from datetime import datetime, timezone

import pytest

from backend.contracts import ExecutionResult
from backend.portfolio import PortfolioManager


def make_execution(
    action="BUY",
    status="FILLED",
    asset="RELIANCE",
    quantity=10.0,
    price=100.0,
    transaction_cost=1.0,
):
    return ExecutionResult(
        status=status,
        asset=asset,
        action=action,
        requested_quantity=quantity,
        executed_quantity=quantity,
        requested_price=price,
        executed_price=price,
        transaction_cost=transaction_cost,
        slippage=0.0,
        timestamp=datetime.now(timezone.utc),
        reason="test",
    )


def test_initial_portfolio_state():
    portfolio = PortfolioManager(initial_cash=10000.0)

    state = portfolio.get_state({})

    assert state.available_cash == 10000.0
    assert state.positions == {}
    assert state.total_value == 10000.0
    assert state.current_exposure == 0.0
    assert state.pnl == 0.0
    assert state.drawdown == 0.0


def test_buy_updates_cash_and_position():
    portfolio = PortfolioManager(initial_cash=10000.0)

    execution = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    state = portfolio.update(
        execution,
        {"RELIANCE": 100.0},
    )

    assert state.available_cash == 8990.0
    assert state.positions["RELIANCE"] == 10.0
    assert state.total_value == 9990.0
    assert state.current_exposure == pytest.approx(0.1001001001)


def test_sell_updates_cash_and_position():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    sell = make_execution(
        action="SELL",
        quantity=5.0,
        price=110.0,
        transaction_cost=5.0,
    )

    state = portfolio.update(
        sell,
        {"RELIANCE": 110.0},
    )

    assert state.available_cash == 9535.0
    assert state.positions["RELIANCE"] == 5.0
    assert state.total_value == 10085.0


def test_sell_entire_position_removes_asset():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    sell = make_execution(
        action="SELL",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    state = portfolio.update(
        sell,
        {"RELIANCE": 100.0},
    )

    assert "RELIANCE" not in state.positions
    assert state.available_cash == 9980.0


def test_sell_cannot_make_position_negative():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=5.0,
        price=100.0,
        transaction_cost=5.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    sell = make_execution(
        action="SELL",
        quantity=6.0,
        price=100.0,
        transaction_cost=5.0,
    )

    with pytest.raises(ValueError, match="position negative"):
        portfolio.update(
            sell,
            {"RELIANCE": 100.0},
        )


def test_buy_cannot_exceed_available_cash():
    portfolio = PortfolioManager(initial_cash=1000.0)

    buy = make_execution(
        action="BUY",
        quantity=20.0,
        price=100.0,
        transaction_cost=10.0,
    )

    with pytest.raises(ValueError, match="Insufficient cash"):
        portfolio.update(
            buy,
            {"RELIANCE": 100.0},
        )


def test_rejected_execution_does_not_change_portfolio():
    portfolio = PortfolioManager(initial_cash=10000.0)

    execution = make_execution(
        action="BUY",
        status="REJECTED",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    state = portfolio.update(
        execution,
        {"RELIANCE": 100.0},
    )

    assert state.available_cash == 10000.0
    assert state.positions == {}
    assert state.total_value == 10000.0


def test_partial_execution_is_applied():
    portfolio = PortfolioManager(initial_cash=10000.0)

    execution = make_execution(
        action="BUY",
        status="PARTIAL",
        quantity=3.0,
        price=100.0,
        transaction_cost=3.0,
    )

    state = portfolio.update(
        execution,
        {"RELIANCE": 100.0},
    )

    assert state.positions["RELIANCE"] == 3.0
    assert state.available_cash == 9697.0


def test_pnl_updates_when_market_price_changes():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    state = portfolio.get_state({"RELIANCE": 120.0})

    assert state.total_value == 10190.0
    assert state.pnl == 190.0


def test_drawdown_is_calculated_from_peak_value():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    high_state = portfolio.get_state({"RELIANCE": 120.0})

    assert high_state.total_value == 10190.0

    low_state = portfolio.get_state({"RELIANCE": 100.0})

    assert low_state.total_value == 9990.0
    assert low_state.drawdown == pytest.approx(
        (10190.0 - 9990.0) / 10190.0
    )


def test_missing_market_price_raises_error():
    portfolio = PortfolioManager(initial_cash=10000.0)

    buy = make_execution(
        action="BUY",
        quantity=10.0,
        price=100.0,
        transaction_cost=10.0,
    )

    portfolio.update(buy, {"RELIANCE": 100.0})

    with pytest.raises(ValueError, match="Missing market price"):
        portfolio.get_state({})


def test_negative_initial_cash_is_rejected():
    with pytest.raises(ValueError, match="initial_cash cannot be negative"):
        PortfolioManager(initial_cash=-1.0)


def test_negative_execution_quantity_is_rejected():
    portfolio = PortfolioManager(initial_cash=10000.0)

    execution = make_execution(
        action="BUY",
        quantity=-1.0,
    )

    with pytest.raises(ValueError, match="executed_quantity cannot be negative"):
        portfolio.update(
            execution,
            {"RELIANCE": 100.0},
        )


def test_unsupported_execution_action_is_rejected():
    portfolio = PortfolioManager(initial_cash=10000.0)

    execution = make_execution(
        action="HOLD",
    )

    with pytest.raises(ValueError, match="Unsupported execution action"):
        portfolio.update(
            execution,
            {"RELIANCE": 100.0},
        )
