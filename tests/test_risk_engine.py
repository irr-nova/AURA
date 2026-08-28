from datetime import datetime, timezone

from backend.contracts import (
    AgentDecision,
    MarketState,
    PortfolioState,
    RiskConstraints,
)
from backend.risk_engine import RiskEngine


def make_market(**overrides):
    data = {
        "asset": "AAPL",
        "price": 215.40,
        "volume": 1_000_000.0,
        "liquidity": 0.90,
        "volatility": 0.20,
        "sentiment": 0.50,
        "news_signal": 0.50,
        "market_regime": "BULL",
        "timestamp": datetime.now(timezone.utc),
        "data_age_seconds": 1.0,
    }
    data.update(overrides)
    return MarketState(**data)


def make_portfolio(**overrides):
    data = {
        "available_cash": 100_000.0,
        "positions": {"AAPL": 20.0},
        "total_value": 200_000.0,
        "current_exposure": 0.20,
        "pnl": 5_000.0,
        "drawdown": 0.05,
        "timestamp": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return PortfolioState(**data)


def make_decision(**overrides):
    data = {
        "action": "BUY",
        "asset": "AAPL",
        "requested_quantity": 10.0,
        "requested_amount": 2_154.0,
        "confidence": 0.80,
        "expected_return": 0.05,
        "reason": "Positive market conditions",
        "timestamp": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return AgentDecision(**data)


def test_valid_buy_is_approved():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(),
        make_market(),
        make_portfolio(),
    )

    assert result.status == "APPROVE"
    assert result.approved_quantity == 10.0
    assert result.approved_amount == 2_154.0


def test_hold_is_approved_with_zero_trade():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            action="HOLD",
            requested_quantity=0.0,
            requested_amount=0.0,
        ),
        make_market(),
        make_portfolio(),
    )

    assert result.status == "APPROVE"
    assert result.approved_quantity == 0.0
    assert result.approved_amount == 0.0


def test_high_volatility_reduces_trade():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(),
        make_market(volatility=0.80),
        make_portfolio(),
    )

    assert result.status in {"MODIFY", "REJECT"}
    assert "MAX_VOLATILITY" in result.constraints_triggered


def test_low_liquidity_is_flagged():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(),
        make_market(liquidity=0.10),
        make_portfolio(),
    )

    assert result.status in {"MODIFY", "REJECT"}
    assert "MIN_LIQUIDITY" in result.constraints_triggered


def test_max_drawdown_rejects_trade():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(),
        make_market(),
        make_portfolio(drawdown=0.20),
    )

    assert result.status == "REJECT"
    assert "MAX_DRAWDOWN" in result.constraints_triggered


def test_sell_cannot_exceed_position():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            action="SELL",
            requested_quantity=50.0,
            requested_amount=10_770.0,
        ),
        make_market(),
        make_portfolio(),
    )

    assert result.status == "REJECT"
    assert "POSITION_LIMIT" in result.constraints_triggered


def test_reduce_cannot_exceed_position():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            action="REDUCE",
            requested_quantity=50.0,
            requested_amount=10_770.0,
        ),
        make_market(),
        make_portfolio(),
    )

    assert result.status == "REJECT"
    assert "POSITION_LIMIT" in result.constraints_triggered


def test_reduce_within_position_is_approved():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            action="REDUCE",
            requested_quantity=5.0,
            requested_amount=1_077.0,
        ),
        make_market(),
        make_portfolio(),
    )

    assert result.status == "APPROVE"
    assert result.approved_quantity == 5.0


def test_buy_above_position_allocation_is_modified():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            requested_quantity=300.0,
            requested_amount=64_620.0,
        ),
        make_market(),
        make_portfolio(),
    )

    assert result.status in {"MODIFY", "REJECT"}
    assert "MAX_POSITION_ALLOCATION" in result.constraints_triggered


def test_buy_above_available_cash_is_modified_or_rejected():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(
            requested_quantity=600.0,
            requested_amount=129_240.0,
        ),
        make_market(),
        make_portfolio(available_cash=50_000.0),
    )

    assert result.status in {"MODIFY", "REJECT"}
    assert "AVAILABLE_CASH" in result.constraints_triggered


def test_asset_mismatch_is_rejected():
    engine = RiskEngine()

    result = engine.evaluate(
        make_decision(asset="TSLA"),
        make_market(asset="AAPL"),
        make_portfolio(),
    )

    assert result.status == "REJECT"
    assert "ASSET_MISMATCH" in result.constraints_triggered


def test_custom_risk_constraints_are_supported():
    constraints = RiskConstraints(
        max_portfolio_exposure=0.50,
        max_single_asset_exposure=0.20,
        max_position_allocation=0.10,
        max_drawdown=0.10,
        max_volatility=0.30,
        min_liquidity=0.50,
    )

    engine = RiskEngine(constraints)

    result = engine.evaluate(
        make_decision(),
        make_market(),
        make_portfolio(),
    )

    assert result.status in {"APPROVE", "MODIFY", "REJECT"}