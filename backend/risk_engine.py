from backend.contracts import RiskDecision


class RiskEngine:
    """
    Independent risk-control layer.

    The risk engine does not decide whether a trade is desirable.
    It only decides whether the agent's proposed trade is safe
    enough to approve.
    """

    MAX_RISK_SCORE = 0.75
    MAX_PORTFOLIO_EXPOSURE = 0.80

    def evaluate(
        self,
        agent_decision,
        market_state,
        portfolio_state,
    ):
        risk_factors = []
        constraints_triggered = []

        action = agent_decision.action
        requested_quantity = float(
            agent_decision.requested_quantity
        )

        price = float(market_state.price)

        portfolio_value = max(
            float(portfolio_state.total_value),
            1.0
        )

        current_exposure = float(
            portfolio_state.current_exposure
        )

        volatility = float(
            market_state.volatility
        )

        confidence = float(
            agent_decision.confidence
        )

        # ----------------------------------------------------
        # Calculate base risk
        # ----------------------------------------------------

        risk_score = 0.0

        risk_score += min(
            volatility,
            1.0
        ) * 0.60

        risk_score += (
            max(0.0, 1.0 - confidence)
            * 0.40
        )

        risk_score = min(
            max(risk_score, 0.0),
            1.0
        )

        # ----------------------------------------------------
        # Risk factors
        # ----------------------------------------------------

        if volatility >= 0.30:
            risk_factors.append(
                "High market volatility"
            )

        if confidence < 0.60:
            risk_factors.append(
                "Agent confidence is relatively low"
            )

        if current_exposure >= 0.70:
            risk_factors.append(
                "Portfolio exposure is elevated"
            )

        # ----------------------------------------------------
        # HOLD
        # ----------------------------------------------------

        if action == "HOLD":

            return RiskDecision(
                status="REJECT",
                risk_score=risk_score,
                approved_quantity=0.0,
                approved_amount=0.0,
                risk_factors=risk_factors,
                constraints_triggered=[
                    "NO_TRADE_REQUESTED"
                ],
            )

        # ----------------------------------------------------
        # Invalid quantity
        # ----------------------------------------------------

        if requested_quantity <= 0:

            return RiskDecision(
                status="REJECT",
                risk_score=risk_score,
                approved_quantity=0.0,
                approved_amount=0.0,
                risk_factors=risk_factors,
                constraints_triggered=[
                    "INVALID_QUANTITY"
                ],
            )

        requested_amount = (
            requested_quantity * price
        )

        # ----------------------------------------------------
        # SELL validation
        # ----------------------------------------------------

        if action in {"SELL", "REDUCE"}:

            current_position = float(
                portfolio_state.positions.get(
                    market_state.asset,
                    0.0
                )
            )

            if current_position <= 0:

                return RiskDecision(
                    status="REJECT",
                    risk_score=risk_score,
                    approved_quantity=0.0,
                    approved_amount=0.0,
                    risk_factors=risk_factors,
                    constraints_triggered=[
                        "NO_POSITION_TO_SELL"
                    ],
                )

            approved_quantity = min(
                requested_quantity,
                current_position
            )

            approved_amount = (
                approved_quantity * price
            )

            if risk_score > self.MAX_RISK_SCORE:

                constraints_triggered.append(
                    "RISK_SCORE_TOO_HIGH"
                )

                return RiskDecision(
                    status="REJECT",
                    risk_score=risk_score,
                    approved_quantity=0.0,
                    approved_amount=0.0,
                    risk_factors=risk_factors,
                    constraints_triggered=constraints_triggered,
                )

            return RiskDecision(
                status="APPROVE",
                risk_score=risk_score,
                approved_quantity=approved_quantity,
                approved_amount=approved_amount,
                risk_factors=risk_factors,
                constraints_triggered=constraints_triggered,
            )

        # ----------------------------------------------------
        # BUY validation
        # ----------------------------------------------------

        if action == "BUY":

            available_cash = float(
                portfolio_state.available_cash
            )

            if requested_amount > available_cash:

                max_quantity = (
                    available_cash / price
                )

                if max_quantity <= 0:

                    return RiskDecision(
                        status="REJECT",
                        risk_score=risk_score,
                        approved_quantity=0.0,
                        approved_amount=0.0,
                        risk_factors=risk_factors,
                        constraints_triggered=[
                            "INSUFFICIENT_CASH"
                        ],
                    )

                approved_quantity = max_quantity

                constraints_triggered.append(
                    "QUANTITY_REDUCED_TO_AVAILABLE_CASH"
                )

            else:

                approved_quantity = requested_quantity

            # ------------------------------------------------
            # Exposure limit
            # ------------------------------------------------

            maximum_position_value = (
                portfolio_value
                * self.MAX_PORTFOLIO_EXPOSURE
            )

            current_position = float(
                portfolio_state.positions.get(
                    market_state.asset,
                    0.0
                )
            )

            current_position_value = (
                current_position * price
            )

            remaining_capacity = (
                maximum_position_value
                - current_position_value
            )

            if remaining_capacity <= 0:

                return RiskDecision(
                    status="REJECT",
                    risk_score=risk_score,
                    approved_quantity=0.0,
                    approved_amount=0.0,
                    risk_factors=risk_factors,
                    constraints_triggered=[
                        "MAX_EXPOSURE_REACHED"
                    ],
                )

            exposure_quantity = (
                remaining_capacity / price
            )

            if approved_quantity > exposure_quantity:

                approved_quantity = exposure_quantity

                constraints_triggered.append(
                    "QUANTITY_REDUCED_TO_EXPOSURE_LIMIT"
                )

            # ------------------------------------------------
            # Risk score check
            # ------------------------------------------------

            if risk_score > self.MAX_RISK_SCORE:

                return RiskDecision(
                    status="REJECT",
                    risk_score=risk_score,
                    approved_quantity=0.0,
                    approved_amount=0.0,
                    risk_factors=risk_factors,
                    constraints_triggered=[
                        "RISK_SCORE_TOO_HIGH"
                    ],
                )

            if approved_quantity <= 0:

                return RiskDecision(
                    status="REJECT",
                    risk_score=risk_score,
                    approved_quantity=0.0,
                    approved_amount=0.0,
                    risk_factors=risk_factors,
                    constraints_triggered=[
                        "ZERO_APPROVED_QUANTITY"
                    ],
                )

            approved_amount = (
                approved_quantity * price
            )

            status = (
                "MODIFY"
                if constraints_triggered
                else "APPROVE"
            )

            return RiskDecision(
                status=status,
                risk_score=risk_score,
                approved_quantity=approved_quantity,
                approved_amount=approved_amount,
                risk_factors=risk_factors,
                constraints_triggered=constraints_triggered,
            )

        # ----------------------------------------------------
        # Unknown action
        # ----------------------------------------------------

        return RiskDecision(
            status="REJECT",
            risk_score=risk_score,
            approved_quantity=0.0,
            approved_amount=0.0,
            risk_factors=risk_factors,
            constraints_triggered=[
                "UNKNOWN_ACTION"
            ],
        )