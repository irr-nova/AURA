from datetime import datetime, timezone

from backend.contracts import AgentDecision, MarketState, PortfolioState
from backend.validation import (
    validate_agent_decision,
    validate_market_state,
    validate_portfolio_state,
)


def make_agent_decision(**overrides):
    data = {
        "action": "BUY",
        "asset": "AAPL",
        "requested_quantity": 10.0,
        "requested_amount": 2154.0,
        "confidence": 0.8,
        "expected_return": 0.05,
        "reason": "Positive market conditions",
        "timestamp": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return AgentDecision(**data)


def make_market_state(**overrides):
    data = {
        "asset": "AAPL",
        "price": 215.40,
        "volume": 1_250_000.0,
        "liquidity": 0.87,
        "volatility": 0.24,
        "sentiment": 0.65,
        "news_signal": 0.72,
        "market_regime": "BULL",
        "timestamp": datetime.now(timezone.utc),
        "data_age_seconds": 2.0,
    }
    data.update(overrides)
    return MarketState(**data)


def make_portfolio_state(**overrides):
    data = {
        "available_cash": 100_000.0,
        "positions": {"AAPL": 20.0},
        "total_value": 200_000.0,
        "current_exposure": 0.25,
        "pnl": 5_000.0,
        "drawdown": 0.05,
        "timestamp": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return PortfolioState(**data)


def test_valid_buy_decision():
    decision = make_agent_decision()

    assert validate_agent_decision(decision) == []


def test_hold_must_have_zero_quantity_and_amount():
    decision = make_agent_decision(
        action="HOLD",
        requested_quantity=10.0,
        requested_amount=2154.0,
    )

    errors = validate_agent_decision(decision)

    assert any("HOLD quantity" in error for error in errors)
    assert any("HOLD amount" in error for error in errors)


def test_reduce_requires_positive_quantity():
    decision = make_agent_decision(
        action="REDUCE",
        requested_quantity=0.0,
        requested_amount=0.0,
    )

    errors = validate_agent_decision(decision)

    assert any("quantity" in error.lower() for error in errors)
    assert any("amount" in error.lower() for error in errors)


def test_confidence_must_be_between_zero_and_one():
    decision = make_agent_decision(confidence=1.5)

    errors = validate_agent_decision(decision)

    assert any("confidence" in error.lower() for error in errors)


def test_market_state_rejects_stale_data():
    market = make_market_state(data_age_seconds=45.0)

    errors = validate_market_state(market)

    assert any("stale" in error.lower() for error in errors)


def test_market_state_rejects_invalid_liquidity():
    market = make_market_state(liquidity=1.5)

    errors = validate_market_state(market)

    assert any("liquidity" in error.lower() for error in errors)


def test_valid_market_state():
    market = make_market_state()

    assert validate_market_state(market) == []


def test_portfolio_rejects_negative_cash():
    portfolio = make_portfolio_state(available_cash=-100.0)

    errors = validate_portfolio_state(portfolio)

    assert any("cash" in error.lower() for error in errors)


def test_portfolio_rejects_invalid_exposure():
    portfolio = make_portfolio_state(current_exposure=1.5)

    errors = validate_portfolio_state(portfolio)

    assert any("exposure" in error.lower() for error in errors)


def test_valid_portfolio_state():
    portfolio = make_portfolio_state()

    assert validate_portfolio_state(portfolio) == []