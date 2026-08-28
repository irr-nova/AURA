from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
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
    data_age_seconds: float


@dataclass(frozen=True)
class PortfolioState:
    available_cash: float
    positions: dict[str, float]
    total_value: float
    current_exposure: float
    pnl: float
    drawdown: float
    timestamp: datetime


@dataclass(frozen=True)
class AgentDecision:
    action: str
    asset: str
    requested_quantity: float
    requested_amount: float
    confidence: float
    expected_return: float
    reason: str
    timestamp: datetime


@dataclass(frozen=True)
class RiskDecision:
    status: str
    approved_quantity: float
    approved_amount: float
    risk_score: float
    risk_factors: list[str]
    constraints_triggered: list[str]
    timestamp: datetime


@dataclass(frozen=True)
class RiskConstraints:
    max_portfolio_exposure: float = 0.70
    max_single_asset_exposure: float = 0.30
    max_position_allocation: float = 0.25
    max_drawdown: float = 0.15
    max_volatility: float = 0.50
    min_liquidity: float = 0.30
    transaction_cost_rate: float = 0.001


@dataclass(frozen=True)
class ApprovedOrder:
    asset: str
    action: str
    approved_quantity: float
    approved_amount: float
    timestamp: datetime


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    asset: str
    action: str
    requested_quantity: float
    executed_quantity: float
    requested_price: float
    executed_price: float
    transaction_cost: float
    slippage: float
    timestamp: datetime
    reason: str

@dataclass(frozen=True)
class AdaptationFeedback:
    execution_outcome: str
    requested_quantity: float
    executed_quantity: float
    requested_price: float
    executed_price: float
    transaction_cost: float
    slippage: float
    resulting_portfolio_value: float
    pnl: float
    drawdown: float
    current_exposure: float
    resulting_position: float
    risk_outcome: str
    timestamp: datetime