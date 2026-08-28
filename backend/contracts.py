from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class MarketState:
    asset: str
    price: float
    volume: float
    liquidity: float
    volatility: float
    sentiment: float
    news_signal: float
    market_regime: str
    timestamp: datetime

    @property
    def data_age_seconds(self) -> float:
        now = datetime.now(timezone.utc)

        timestamp = self.timestamp

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return max(
            0.0,
            (now - timestamp).total_seconds()
        )


@dataclass
class AgentDecision:
    action: str
    confidence: float
    expected_return: float
    requested_quantity: float
    reason: str


@dataclass
class RiskDecision:
    status: str
    risk_score: float
    approved_quantity: float
    approved_amount: float
    risk_factors: List[str] = field(
        default_factory=list
    )
    constraints_triggered: List[str] = field(
        default_factory=list
    )


@dataclass
class ApprovedOrder:
    asset: str
    action: str
    approved_quantity: float
    approved_amount: float
    timestamp: datetime


@dataclass
class ExecutionResult:
    status: str
    asset: str
    action: str
    executed_quantity: float
    executed_price: float
    slippage: float
    transaction_cost: float
    timestamp: datetime


@dataclass
class PortfolioState:
    available_cash: float
    positions: Dict[str, float]
    total_value: float
    current_exposure: float
    pnl: float
    drawdown: float
    timestamp: datetime


@dataclass
class AdaptationFeedback:
    execution_outcome: str
    risk_outcome: str
    resulting_position: float
    pnl: float
    drawdown: float