from backend.contracts import AgentDecision


class AutonomousAgent:
    """
    Generates a trading decision from the current market state
    and portfolio state.

    This is a simple rule-based agent for the AURA prototype.
    """

    def decide(self, market_state, portfolio_state):
        sentiment = float(market_state.sentiment)
        news_signal = float(market_state.news_signal)
        volatility = float(market_state.volatility)

        # Combined market signal.
        signal = (
            sentiment * 0.50
            + news_signal * 0.30
            - volatility * 0.20
        )

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if signal > 0.25:

            action = "BUY"
            confidence = min(
                0.95,
                0.60 + abs(signal) * 0.30
            )

            expected_return = signal

            requested_quantity = max(
                1.0,
                min(
                    100.0,
                    portfolio_state.available_cash
                    / market_state.price
                    * 0.10
                )
            )

            reason = (
                f"{market_state.asset} shows constructive "
                f"market conditions. Sentiment and news signals "
                f"are supporting a potential upward move."
            )

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        elif signal < -0.25:

            current_position = float(
                portfolio_state.positions.get(
                    market_state.asset,
                    0.0
                )
            )

            if current_position > 0:

                action = "SELL"

                confidence = min(
                    0.95,
                    0.60 + abs(signal) * 0.30
                )

                expected_return = signal

                requested_quantity = min(
                    current_position,
                    max(
                        1.0,
                        current_position * 0.25
                    )
                )

                reason = (
                    f"{market_state.asset} shows weakening "
                    f"market conditions. Negative sentiment "
                    f"and news signals suggest reducing exposure."
                )

            else:

                action = "HOLD"
                confidence = 0.65
                expected_return = signal
                requested_quantity = 0.0

                reason = (
                    f"{market_state.asset} has a negative market "
                    f"signal, but there is no existing position "
                    f"available to sell."
                )

        # ----------------------------------------------------
        # HOLD
        # ----------------------------------------------------

        else:

            action = "HOLD"
            confidence = 0.60
            expected_return = signal
            requested_quantity = 0.0

            reason = (
                f"{market_state.asset} is currently showing "
                f"mixed market conditions. AURA recommends "
                f"waiting for a stronger signal."
            )

        return AgentDecision(
            action=action,
            confidence=confidence,
            expected_return=expected_return,
            requested_quantity=requested_quantity,
            reason=reason,
        )