from datetime import datetime, timezone

from .contracts import AgentDecision, MarketState, PortfolioState


VALID_ACTIONS = {"BUY", "SELL", "HOLD", "REDUCE"}

MIN_DATA_AGE_SECONDS = 30.0


def validate_agent_decision(decision: AgentDecision) -> list[str]:
    """
    Validate the structure and basic values of an AgentDecision.

    Returns:
        A list of validation errors.
        An empty list means the decision is valid.
    """
    errors: list[str] = []

    if decision.action not in VALID_ACTIONS:
        errors.append(f"Invalid action: {decision.action}")

    if not decision.asset or decision.asset != decision.asset.upper():
        errors.append("Asset must be a non-empty uppercase ticker.")

    if decision.requested_quantity < 0:
        errors.append("Requested quantity cannot be negative.")

    if decision.requested_amount < 0:
        errors.append("Requested amount cannot be negative.")

    if not 0.0 <= decision.confidence <= 1.0:
        errors.append("Confidence must be between 0 and 1.")

    if decision.action in {"BUY", "SELL", "REDUCE"}:
        if decision.requested_quantity <= 0:
            errors.append(
                "Trade quantity must be greater than zero for "
                "BUY, SELL, or REDUCE."
            )

        if decision.requested_amount <= 0:
            errors.append(
                "Trade amount must be greater than zero for "
                "BUY, SELL, or REDUCE."
            )

    if decision.action == "HOLD":
        if decision.requested_quantity != 0:
            errors.append("HOLD quantity must be zero.")

        if decision.requested_amount != 0:
            errors.append("HOLD amount must be zero.")

    if not isinstance(decision.timestamp, datetime):
        errors.append("Decision timestamp must be a datetime.")

    return errors


def validate_market_state(market: MarketState) -> list[str]:
    """
    Validate the current market observation.

    Returns:
        A list of validation errors.
        An empty list means the market state is valid.
    """
    errors: list[str] = []

    if not market.asset or market.asset != market.asset.upper():
        errors.append("Market asset must be a non-empty uppercase ticker.")

    if market.price <= 0:
        errors.append("Market price must be greater than zero.")

    if market.volume < 0:
        errors.append("Market volume cannot be negative.")

    if not 0.0 <= market.liquidity <= 1.0:
        errors.append("Liquidity must be between 0 and 1.")

    if market.volatility < 0:
        errors.append("Volatility cannot be negative.")

    if not -1.0 <= market.sentiment <= 1.0:
        errors.append("Sentiment must be between -1 and 1.")

    if not -1.0 <= market.news_signal <= 1.0:
        errors.append("News signal must be between -1 and 1.")

    if market.data_age_seconds < 0:
        errors.append("Data age cannot be negative.")

    if market.data_age_seconds > MIN_DATA_AGE_SECONDS:
        errors.append(
            f"Market data is stale: {market.data_age_seconds:.2f} seconds old."
        )

    if not isinstance(market.timestamp, datetime):
        errors.append("Market timestamp must be a datetime.")

    return errors


def validate_portfolio_state(portfolio: PortfolioState) -> list[str]:
    """
    Validate the current portfolio state.

    Returns:
        A list of validation errors.
        An empty list means the portfolio state is valid.
    """
    errors: list[str] = []

    if portfolio.available_cash < 0:
        errors.append("Available cash cannot be negative.")

    if portfolio.total_value <= 0:
        errors.append("Total portfolio value must be greater than zero.")

    if not 0.0 <= portfolio.current_exposure <= 1.0:
        errors.append("Current exposure must be between 0 and 1.")

    if not 0.0 <= portfolio.drawdown <= 1.0:
        errors.append("Drawdown must be between 0 and 1.")

    for asset, quantity in portfolio.positions.items():
        if not asset or asset != asset.upper():
            errors.append(
                f"Invalid portfolio asset identifier: {asset}"
            )

        if quantity < 0:
            errors.append(
                f"Position quantity cannot be negative: {asset}"
            )

    if not isinstance(portfolio.timestamp, datetime):
        errors.append("Portfolio timestamp must be a datetime.")

    return errors