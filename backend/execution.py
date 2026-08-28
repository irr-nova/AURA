from datetime import datetime, timezone

from backend.contracts import ExecutionResult


class ExecutionEngine:

    def execute(
        self,
        approved_order,
        market_price,
    ):

        market_price = float(market_price)

        # Small simulated slippage
        slippage = market_price * 0.001

        if approved_order.action == "BUY":
            execution_price = (
                market_price + slippage
            )
        else:
            execution_price = (
                market_price - slippage
            )

        quantity = float(
            approved_order.approved_quantity
        )

        transaction_cost = (
            quantity *
            execution_price *
            0.001
        )

        return ExecutionResult(
            status="EXECUTED",
            action=approved_order.action,
            asset=approved_order.asset,
            executed_quantity=quantity,
            executed_price=execution_price,
            slippage=slippage,
            transaction_cost=transaction_cost,
            timestamp=datetime.now(timezone.utc),
        )