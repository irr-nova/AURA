from datetime import datetime, timezone

from backend.agent import AutonomousAgent
from backend.contracts import MarketState, PortfolioState


def make_market(
    *,
    liquidity=0.87,
    volatility=0.24,
    sentiment=0.65,
    news_signal=0.72,
    data_age_seconds=0.0,
):
    return MarketState(
        asset="AAPL",
        price=215.40,
        volume=1_250_000.0,
        liquidity=liquidity,
        volatility=volatility,
        sentiment=sentiment,
        news_signal=news_signal,
        market_regime="BULL",
        timestamp=datetime.now(timezone.utc),
        data_age_seconds=data_age_seconds,
    )


def make_portfolio(
    *,
    cash=800_000.0,
    positions=None,
):
    positions = positions or {}

    return PortfolioState(
        available_cash=cash,
        positions=positions,
        total_value=1_000_000.0,
        current_exposure=0.0,
        pnl=0.0,
        drawdown=0.0,
        timestamp=datetime.now(timezone.utc),
    )


def test_strong_market_produces_buy():
    agent = AutonomousAgent()

    decision = agent.decide(
        make_market(),
        make_portfolio(),
    )

    assert decision.action == "BUY"
    assert decision.asset == "AAPL"
    assert decision.requested_quantity > 0
    assert decision.requested_amount > 0


def test_stale_market_produces_hold():
    agent = AutonomousAgent()

    decision = agent.decide(
        make_market(data_age_seconds=120.0),
        make_portfolio(),
    )

    assert decision.action == "HOLD"
    assert decision.requested_quantity == 0


def test_high_volatility_reduces_existing_position():
    agent = AutonomousAgent()

    decision = agent.decide(
        make_market(
            volatility=0.60,
            sentiment=-0.40,
            news_signal=-0.30,
        ),
        make_portfolio(
            positions={"AAPL": 100.0},
        ),
    )

    assert decision.action == "REDUCE"
    assert decision.requested_quantity > 0
    assert decision.requested_quantity <= 100.0


def test_low_liquidity_holds_without_position():
    agent = AutonomousAgent()

    decision = agent.decide(
        make_market(liquidity=0.20),
        make_portfolio(),
    )

    assert decision.action == "HOLD"
    assert decision.requested_quantity == 0


def test_no_cash_cannot_buy():
    agent = AutonomousAgent()

    decision = agent.decide(
        make_market(),
        make_portfolio(cash=0.0),
    )

    assert decision.action == "HOLD"
    assert decision.requested_quantity == 0