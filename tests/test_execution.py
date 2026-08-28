from datetime import datetime, timezone

import pytest

from backend.contracts import ApprovedOrder
from backend.execution import ExecutionEngine


def make_order(
    action="BUY",
    asset="RELIANCE",
    quantity=10.0,
    amount=1000.0,
):
    return ApprovedOrder(
        asset=asset,
        action=action,
        approved_quantity=quantity,
        approved_amount=amount,
        timestamp=datetime.now(timezone.utc),
    )


def test_buy_order_is_executed():
    engine = ExecutionEngine(
        transaction_cost_rate=0.001,
        slippage_rate=0.0005,
    )

    order = make_order(
        action="BUY",
        quantity=10.0,
        amount=1000.0,
    )

    result = engine.execute(order, market_price=100.0)

    assert result.status == "FILLED"
    assert result.asset == "RELIANCE"
    assert result.action == "BUY"
    assert result.requested_quantity == 10.0
    assert result.executed_quantity == 10.0
    assert result.requested_price == 100.0
    assert result.executed_price == pytest.approx(100.05)
    assert result.transaction_cost == pytest.approx(1.0005)
    assert result.slippage == pytest.approx(0.05)


def test_sell_order_is_executed():
    engine = ExecutionEngine(
        transaction_cost_rate=0.001,
        slippage_rate=0.0005,
    )

    order = make_order(
        action="SELL",
        quantity=10.0,
        amount=1000.0,
    )

    result = engine.execute(order, market_price=100.0)

    assert result.status == "FILLED"
    assert result.action == "SELL"
    assert result.executed_quantity == 10.0
    assert result.executed_price == pytest.approx(99.95)
    assert result.transaction_cost == pytest.approx(0.9995)
    assert result.slippage == pytest.approx(0.05)


def test_execution_only_accepts_buy_or_sell():
    engine = ExecutionEngine()

    order = make_order(action="HOLD")

    with pytest.raises(
        ValueError,
        match="Unsupported execution action",
    ):
        engine.execute(order, market_price=100.0)


def test_reduce_is_not_accepted_by_execution():
    engine = ExecutionEngine()

    order = make_order(action="REDUCE")

    with pytest.raises(
        ValueError,
        match="Unsupported execution action",
    ):
        engine.execute(order, market_price=100.0)


def test_zero_quantity_is_rejected():
    engine = ExecutionEngine()

    order = make_order(quantity=0.0)

    with pytest.raises(
        ValueError,
        match="approved_quantity must be greater than zero",
    ):
        engine.execute(order, market_price=100.0)


def test_negative_quantity_is_rejected():
    engine = ExecutionEngine()

    order = make_order(quantity=-5.0)

    with pytest.raises(
        ValueError,
        match="approved_quantity must be greater than zero",
    ):
        engine.execute(order, market_price=100.0)


def test_invalid_market_price_is_rejected():
    engine = ExecutionEngine()

    order = make_order()

    with pytest.raises(
        ValueError,
        match="market_price must be greater than zero",
    ):
        engine.execute(order, market_price=0.0)


def test_negative_transaction_cost_rate_is_rejected():
    with pytest.raises(
        ValueError,
        match="transaction_cost_rate cannot be negative",
    ):
        ExecutionEngine(transaction_cost_rate=-0.001)


def test_negative_slippage_rate_is_rejected():
    with pytest.raises(
        ValueError,
        match="slippage_rate cannot be negative",
    ):
        ExecutionEngine(slippage_rate=-0.001)


def test_execution_result_has_utc_timestamp():
    engine = ExecutionEngine()

    order = make_order()

    result = engine.execute(order, market_price=100.0)

    assert result.timestamp.tzinfo == timezone.utc