from datetime import datetime, timezone

from backend.contracts import ExecutionResult, PortfolioState


class PortfolioManager:
    """Maintains portfolio state based on executed trades."""

    def __init__(self, initial_cash: float):
        if initial_cash < 0:
            raise ValueError(
                "initial_cash cannot be negative"
            )

        self._initial_portfolio_value = float(
            initial_cash
        )

        self._peak_portfolio_value = float(
            initial_cash
        )

        self._available_cash = float(
            initial_cash
        )

        self._positions: dict[str, float] = {}

    # --------------------------------------------------------
    # PUBLIC READ-ONLY ACCESS
    # --------------------------------------------------------

    @property
    def positions(self) -> dict[str, float]:
        """
        Return a copy of the current positions.

        This keeps the internal _positions dictionary protected
        while allowing the UI and diagnostics to inspect it.
        """
        return dict(self._positions)

    @property
    def available_cash(self) -> float:
        """Return currently available cash."""
        return self._available_cash

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        execution_result: ExecutionResult,
        market_prices: dict[str, float],
    ) -> PortfolioState:
        """
        Apply a filled or partially filled execution
        and return the resulting portfolio state.
        """

        if execution_result.status not in {
            "FILLED",
            "PARTIAL",
        }:
            return self.get_state(
                market_prices
            )

        asset = execution_result.asset
        action = execution_result.action.upper()

        quantity = float(
            execution_result.executed_quantity
        )

        price = float(
            execution_result.executed_price
        )

        transaction_cost = float(
            execution_result.transaction_cost
        )

        if quantity < 0:
            raise ValueError(
                "executed_quantity cannot be negative"
            )

        if price < 0:
            raise ValueError(
                "executed_price cannot be negative"
            )

        if transaction_cost < 0:
            raise ValueError(
                "transaction_cost cannot be negative"
            )

        trade_value = (
            quantity * price
        )

        current_position = float(
            self._positions.get(
                asset,
                0.0,
            )
        )

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if action == "BUY":

            total_cost = (
                trade_value
                + transaction_cost
            )

            if total_cost > (
                self._available_cash + 1e-9
            ):
                raise ValueError(
                    "Insufficient cash for executed BUY"
                )

            self._available_cash -= total_cost

            self._positions[asset] = (
                current_position
                + quantity
            )

        # ----------------------------------------------------
        # SELL / REDUCE
        # ----------------------------------------------------

        elif action in {
            "SELL",
            "REDUCE",
        }:

            if quantity > (
                current_position + 1e-9
            ):
                raise ValueError(
                    "Executed SELL would make "
                    "the position negative"
                )

            self._available_cash += (
                trade_value
                - transaction_cost
            )

            new_position = (
                current_position
                - quantity
            )

            if abs(new_position) < 1e-9:

                self._positions.pop(
                    asset,
                    None,
                )

            else:

                self._positions[asset] = (
                    new_position
                )

        else:

            raise ValueError(
                "Unsupported execution action: "
                f"{execution_result.action}"
            )

        return self.get_state(
            market_prices
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def get_state(
        self,
        market_prices: dict[str, float],
    ) -> PortfolioState:
        """
        Calculate and return the current immutable
        PortfolioState.
        """

        position_value = 0.0

        for asset, quantity in (
            self._positions.items()
        ):

            if asset not in market_prices:
                raise ValueError(
                    f"Missing market price for {asset}"
                )

            price = float(
                market_prices[asset]
            )

            if price < 0:
                raise ValueError(
                    "Market price cannot be "
                    f"negative for {asset}"
                )

            position_value += (
                float(quantity) * price
            )

        total_value = (
            self._available_cash
            + position_value
        )

        if total_value > 0:

            current_exposure = (
                position_value
                / total_value
            )

        else:

            current_exposure = 0.0

        self._peak_portfolio_value = max(
            self._peak_portfolio_value,
            total_value,
        )

        pnl = (
            total_value
            - self._initial_portfolio_value
        )

        if self._peak_portfolio_value > 0:

            drawdown = (
                self._peak_portfolio_value
                - total_value
            ) / self._peak_portfolio_value

        else:

            drawdown = 0.0

        return PortfolioState(
            available_cash=self._available_cash,
            positions=dict(
                self._positions
            ),
            total_value=total_value,
            current_exposure=current_exposure,
            pnl=pnl,
            drawdown=drawdown,
            timestamp=datetime.now(
                timezone.utc
            ),
        )