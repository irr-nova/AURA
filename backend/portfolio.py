from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PortfolioState:
    available_cash: float
    positions: dict
    total_value: float
    current_exposure: float
    pnl: float
    drawdown: float
    timestamp: datetime


class PortfolioManager:
    """
    Manages portfolio cash, positions and valuation.

    Portfolio valuation uses the prices supplied by the app.
    It never assumes that AAPL is the only asset.
    """

    def __init__(self, initial_cash=100000.0):
        self.initial_cash = float(initial_cash)
        self.available_cash = float(initial_cash)
        self.positions = {}

    def get_state(self, market_prices):
        """
        Calculate the current portfolio state.

        market_prices must contain a valid price for every
        non-zero position.
        """

        market_prices = market_prices or {}

        holdings_value = 0.0

        for asset, quantity in self.positions.items():
            quantity = float(quantity)

            if quantity == 0:
                continue

            if asset not in market_prices:
                raise ValueError(
                    f"Missing market price for {asset}"
                )

            price = float(market_prices[asset])

            if price <= 0:
                raise ValueError(
                    f"Invalid market price for {asset}: {price}"
                )

            holdings_value += quantity * price

        total_value = self.available_cash + holdings_value

        if total_value > 0:
            current_exposure = holdings_value / total_value
        else:
            current_exposure = 0.0

        pnl = total_value - self.initial_cash

        if self.initial_cash > 0:
            drawdown = min(0.0, pnl / self.initial_cash)
        else:
            drawdown = 0.0

        return PortfolioState(
            available_cash=self.available_cash,
            positions=dict(self.positions),
            total_value=total_value,
            current_exposure=current_exposure,
            pnl=pnl,
            drawdown=drawdown,
            timestamp=datetime.now(timezone.utc),
        )

    def update(self, execution_result, market_prices):
        """
        Apply an executed trade and immediately revalue
        the portfolio using the supplied market prices.
        """

        asset = execution_result.asset
        action = execution_result.action.upper()
        quantity = float(execution_result.executed_quantity)
        executed_price = float(execution_result.executed_price)
        transaction_cost = float(
            getattr(execution_result, "transaction_cost", 0.0)
        )

        if quantity <= 0:
            raise ValueError("Executed quantity must be positive.")

        trade_value = quantity * executed_price

        if action == "BUY":
            total_cost = trade_value + transaction_cost

            if total_cost > self.available_cash:
                raise ValueError(
                    "Insufficient cash for BUY order."
                )

            self.available_cash -= total_cost

            self.positions[asset] = (
                self.positions.get(asset, 0.0) + quantity
            )

        elif action == "SELL":
            current_quantity = self.positions.get(asset, 0.0)

            if quantity > current_quantity:
                raise ValueError(
                    f"Cannot sell {quantity} shares of {asset}. "
                    f"Current position is {current_quantity}."
                )

            self.available_cash += (
                trade_value - transaction_cost
            )

            new_quantity = current_quantity - quantity

            if abs(new_quantity) < 1e-9:
                self.positions.pop(asset, None)
            else:
                self.positions[asset] = new_quantity

        else:
            raise ValueError(
                f"Unsupported execution action: {action}"
            )

        return self.get_state(market_prices)