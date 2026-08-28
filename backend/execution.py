from datetime import datetime, timezone

from backend.contracts import ApprovedOrder, ExecutionResult


class ExecutionEngine:
    """Executes approved orders and returns ExecutionResult."""

    def __init__(
        self,
        transaction_cost_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ):
        if transaction_cost_rate < 0:
            raise ValueError("transaction_cost_rate cannot be negative")

        if slippage_rate < 0:
            raise ValueError("slippage_rate cannot be negative")

        self.transaction_cost_rate = float(transaction_cost_rate)
        self.slippage_rate = float(slippage_rate)

    def execute(
        self,
        order: ApprovedOrder,
        market_price: float,
    ) -> ExecutionResult:
        """Execute an approved BUY or SELL order."""

        if order.action not in {"BUY", "SELL"}:
            raise ValueError(
                f"Unsupported execution action: {order.action}"
            )

        if order.approved_quantity <= 0:
            raise ValueError(
                "approved_quantity must be greater than zero"
            )

        if order.approved_amount < 0:
            raise ValueError(
                "approved_amount cannot be negative"
            )

        if market_price <= 0:
            raise ValueError(
                "market_price must be greater than zero"
            )

        quantity = float(order.approved_quantity)
        market_price = float(market_price)

        if order.action == "BUY":
            executed_price = market_price * (1 + self.slippage_rate)
        else:
            executed_price = market_price * (1 - self.slippage_rate)

        trade_value = quantity * executed_price
        transaction_cost = trade_value * self.transaction_cost_rate

        slippage = abs(executed_price - market_price)

        return ExecutionResult(
            status="FILLED",
            asset=order.asset,
            action=order.action,
            requested_quantity=quantity,
            executed_quantity=quantity,
            requested_price=market_price,
            executed_price=executed_price,
            transaction_cost=transaction_cost,
            slippage=slippage,
            timestamp=datetime.now(timezone.utc),
            reason="Order executed successfully",
        )