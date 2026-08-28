import os
from datetime import datetime, timezone

import streamlit as st

from backend.market_data import MarketDataProvider
from backend.market_simulator import MarketSimulator
from backend.agent import AutonomousAgent
from backend.portfolio import PortfolioManager
from backend.risk_engine import RiskEngine
from backend.execution import ExecutionEngine
from backend.adaptation import AdaptationManager
from backend.contracts import ApprovedOrder


st.set_page_config(
    page_title="AURA — Autonomous Market Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SERVICES
# ============================================================

@st.cache_resource
def get_market_provider():

    return MarketDataProvider(
        MarketSimulator()
    )


@st.cache_resource
def get_agent():

    return AutonomousAgent()


@st.cache_resource
def get_risk_engine():

    return RiskEngine()


@st.cache_resource
def get_execution_engine():

    return ExecutionEngine()


@st.cache_resource
def get_adaptation_manager():

    return AdaptationManager()


provider = get_market_provider()
agent = get_agent()
risk_engine = get_risk_engine()
execution_engine = get_execution_engine()
adaptation_manager = get_adaptation_manager()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #050505;
        color: #F2F0E8;
    }

    [data-testid="stAppViewContainer"] {
        background: #050505;
    }

    [data-testid="stSidebar"] {
        background: #090909;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
    }

    .aura-title {
        color: #D4AF37;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: .18em;
    }

    .subtitle {
        color: #888;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .section {
        color: #D4AF37;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .15em;
        margin-top: 2rem;
        margin-bottom: .8rem;
    }

    .card {
        background: #0C0C0C;
        border: 1px solid #282828;
        border-radius: 5px;
        padding: 1.2rem;
        min-height: 120px;
    }

    .label {
        color: #777;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
    }

    .value {
        color: #F2F0E8;
        font-size: 1.7rem;
        font-weight: 700;
        margin-top: .5rem;
    }

    .gold {
        color: #D4AF37;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "# AURA"
    )

    st.caption(
        "AUTONOMOUS MARKET INTELLIGENCE"
    )

    selected_asset = st.selectbox(
        "Select Asset",
        ["AAPL", "TSLA", "NVDA"],
    )

    initial_cash = st.number_input(
        "Portfolio Capital",
        min_value=1000.0,
        max_value=10_000_000.0,
        value=100_000.0,
        step=1000.0,
    )

    if st.button(
        "↻ Refresh Market Data",
        use_container_width=True,
    ):
        st.rerun()

    if st.button(
        "Reset Portfolio",
        use_container_width=True,
    ):

        st.session_state.pop(
            "portfolio_manager",
            None,
        )

        st.rerun()

    st.markdown("---")

    st.markdown(
        "**SYSTEM STATUS**"
    )

    st.success("● ONLINE")

    st.caption(
        "Pipeline: AUTONOMOUS"
    )

    st.caption(
        "Data Source: MARKET SIMULATOR"
    )

    st.caption(
        "Currency: INR"
    )


# ============================================================
# PORTFOLIO
# ============================================================

if (
    "portfolio_manager" not in st.session_state
    or
    st.session_state.get(
        "portfolio_initial_cash"
    ) != initial_cash
):

    st.session_state[
        "portfolio_manager"
    ] = PortfolioManager(
        initial_cash=initial_cash
    )

    st.session_state[
        "portfolio_initial_cash"
    ] = initial_cash


portfolio_manager = st.session_state[
    "portfolio_manager"
]


# ============================================================
# MARKET HELPERS
# ============================================================

def safe_get_market_state(asset):
    """
    Safely retrieve market state for an asset.
    """

    try:
        state = provider.get_market_state(asset)

        if state is None:
            return None

        if not hasattr(state, "price"):
            return None

        if state.price is None:
            return None

        price = float(state.price)

        if price <= 0:
            return None

        return state

    except Exception as exc:
        st.error(
            f"Market data error for {asset}: {exc}"
        )
        return None


def build_portfolio_market_prices(
    portfolio,
    selected_asset,
    selected_state,
):

    prices = {}

    # Selected asset is always available
    if selected_state is not None:

        prices[
            selected_asset
        ] = float(
            selected_state.price
        )

    positions = (
        getattr(
            portfolio,
            "positions",
            {}
        )
        or {}
    )

    # Only assets that are actually held
    # need portfolio valuation.
    for asset, quantity in positions.items():

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            continue

        if quantity == 0:
            continue

        asset = asset.upper()

        if asset in prices:
            continue

        state = safe_get_market_state(
            asset
        )

        if state is not None:

            prices[asset] = float(
                state.price
            )

    return prices


def get_missing_portfolio_assets(
    portfolio,
    market_prices,
):

    missing = []

    positions = (
        getattr(
            portfolio,
            "positions",
            {}
        )
        or {}
    )

    for asset, quantity in positions.items():

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            continue

        if quantity == 0:
            continue

        if asset.upper() not in market_prices:
            missing.append(
                asset.upper()
            )

    return missing


# ============================================================
# MARKET STATE
# ============================================================

market_state = safe_get_market_state(
    selected_asset
)

if market_state is None:

    st.error(
        f"Market data unavailable for "
        f"{selected_asset}."
    )

    st.stop()


# ============================================================
# PRICE MAP
# ============================================================

market_prices = (
    build_portfolio_market_prices(
        portfolio_manager,
        selected_asset,
        market_state,
    )
)


# ============================================================
# VALIDATION
# ============================================================

missing_assets = (
    get_missing_portfolio_assets(
        portfolio_manager,
        market_prices,
    )
)


if missing_assets:

    st.error(
        "Portfolio valuation unavailable: "
        "missing market price for "
        + ", ".join(missing_assets)
    )

    with st.expander(
        "Portfolio valuation diagnostics"
    ):

        st.write(
            "Positions"
        )

        st.json(
            portfolio_manager.positions
        )

        st.write(
            "Market prices"
        )

        st.json(
            market_prices
        )

        st.write(
            "Missing prices"
        )

        st.json(
            missing_assets
        )

    st.stop()


# ============================================================
# PORTFOLIO STATE
# ============================================================

try:

    portfolio_state = (
        portfolio_manager.get_state(
            market_prices
        )
    )

except Exception as exc:

    st.error(
        f"Portfolio valuation error: {exc}"
    )

    with st.expander(
        "Valuation diagnostics"
    ):

        st.json(
            portfolio_manager.positions
        )

        st.json(
            market_prices
        )

    st.stop()


# ============================================================
# AGENT
# ============================================================

agent_decision = agent.decide(
    market_state,
    portfolio_state,
)


# ============================================================
# RISK
# ============================================================

risk_decision = risk_engine.evaluate(
    agent_decision,
    market_state,
    portfolio_state,
)


# ============================================================
# EXECUTION VARIABLES
# ============================================================

execution_result = None
execution_error = None
adaptation_feedback = None
reassessment = None
updated_portfolio = portfolio_state


# ============================================================
# EXECUTION
# ============================================================

if (
    risk_decision.status
    in {"APPROVE", "MODIFY"}
    and
    risk_decision.approved_quantity > 0
    and
    agent_decision.action
    in {"BUY", "SELL"}
):

    approved_order = ApprovedOrder(
        asset=market_state.asset,
        action=agent_decision.action,
        approved_quantity=(
            risk_decision.approved_quantity
        ),
        approved_amount=(
            risk_decision.approved_amount
        ),
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    try:

        execution_result = (
            execution_engine.execute(
                approved_order,
                market_state.price,
            )
        )

        # Update portfolio
        updated_portfolio = (
            portfolio_manager.update(
                execution_result,
                market_prices,
            )
        )

        # Rebuild prices after trade
        final_market_prices = (
            build_portfolio_market_prices(
                portfolio_manager,
                selected_asset,
                market_state,
            )
        )

        final_market_prices[
            market_state.asset
        ] = float(
            market_state.price
        )

        # Final valuation
        updated_portfolio = (
            portfolio_manager.get_state(
                final_market_prices
            )
        )

        market_prices = (
            final_market_prices
        )

        resulting_position = (
            updated_portfolio.positions.get(
                market_state.asset,
                0.0,
            )
        )

        adaptation_feedback = (
            adaptation_manager.create_feedback(
                execution_result,
                updated_portfolio,
                risk_decision,
                resulting_position,
            )
        )

        reassessment = agent.decide(
            market_state,
            updated_portfolio,
        )

    except Exception as exc:

        execution_error = str(exc)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="aura-title">AURA</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Autonomous Unified Risk & Allocation — '
    'Market Intelligence'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# MARKET
# ============================================================

st.markdown(
    '<div class="section">01 / MARKET STATE</div>',
    unsafe_allow_html=True,
)

st.subheader(
    f"{market_state.asset} — Live Market State"
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Price</div>
            <div class="value gold">
                ₹{market_state.price:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c2:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Volume</div>
            <div class="value">
                {market_state.volume:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c3:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Liquidity</div>
            <div class="value">
                {market_state.liquidity:.2%}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c4:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Volatility</div>
            <div class="value">
                {market_state.volatility:.2%}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIGNALS
# ============================================================

st.markdown(
    '<div class="section">02 / MARKET SIGNALS</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Sentiment",
        f"{market_state.sentiment:.2f}",
    )

with c2:

    st.metric(
        "News Signal",
        f"{market_state.news_signal:.2f}",
    )

with c3:

    st.metric(
        "Market Regime",
        market_state.market_regime,
    )


# ============================================================
# PIPELINE
# ============================================================

st.markdown(
    '<div class="section">03 / AUTONOMOUS PIPELINE</div>',
    unsafe_allow_html=True,
)

pipeline = st.columns(6)

pipeline[0].metric(
    "MARKET",
    "LIVE",
    market_state.asset,
)

pipeline[1].metric(
    "AGENT",
    agent_decision.action,
    f"{agent_decision.confidence:.1%}",
)

pipeline[2].metric(
    "RISK",
    risk_decision.status,
    f"{risk_decision.risk_score:.2f}",
)

pipeline[3].metric(
    "EXECUTION",
    (
        execution_result.status
        if execution_result
        else "SKIPPED"
    ),
)

pipeline[4].metric(
    "PORTFOLIO",
    (
        "UPDATED"
        if execution_result
        else "UNCHANGED"
    ),
    f"₹{updated_portfolio.total_value:,.0f}",
)

pipeline[5].metric(
    "ADAPTATION",
    (
        "COMPLETE"
        if adaptation_feedback
        else "WAITING"
    ),
)


# ============================================================
# AGENT DECISION
# ============================================================

st.markdown(
    '<div class="section">04 / AGENT DECISION</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns([1, 2])

with c1:

    st.metric(
        "Recommended Action",
        agent_decision.action,
    )

    st.metric(
        "Confidence",
        f"{agent_decision.confidence:.1%}",
    )

    st.metric(
        "Proposed Quantity",
        f"{agent_decision.requested_quantity:.0f}",
    )

with c2:

    st.info(
        agent_decision.reason
    )


# ============================================================
# RISK
# ============================================================

st.markdown(
    '<div class="section">05 / RISK ENGINE</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Risk Decision",
        risk_decision.status,
    )

with c2:
    st.metric(
        "Risk Score",
        f"{risk_decision.risk_score:.2f}",
    )

with c3:
    st.metric(
        "Approved Amount",
        f"₹{risk_decision.approved_amount:,.2f}",
    )

if risk_decision.risk_factors:

    with st.expander(
        "Risk Factors"
    ):

        for factor in risk_decision.risk_factors:
            st.write(
                f"• {factor}"
            )


# ============================================================
# EXECUTION
# ============================================================

st.markdown(
    '<div class="section">06 / EXECUTION</div>',
    unsafe_allow_html=True,
)

if execution_result:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Status",
        execution_result.status,
    )

    c2.metric(
        "Quantity",
        f"{execution_result.executed_quantity:.0f}",
    )

    c3.metric(
        "Execution Price",
        f"₹{execution_result.executed_price:,.2f}",
    )

    c4.metric(
        "Transaction Cost",
        f"₹{execution_result.transaction_cost:,.2f}",
    )

elif execution_error:

    st.error(
        f"Execution failed: {execution_error}"
    )

else:

    st.info(
        "No trade was executed during this cycle."
    )


# ============================================================
# PORTFOLIO
# ============================================================

st.markdown(
    '<div class="section">07 / PORTFOLIO STATE</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Portfolio Value",
    f"₹{updated_portfolio.total_value:,.2f}",
)

c2.metric(
    "Available Cash",
    f"₹{updated_portfolio.available_cash:,.2f}",
)

c3.metric(
    "Exposure",
    f"{updated_portfolio.current_exposure:.2%}",
)

c4.metric(
    "P&L",
    f"₹{updated_portfolio.pnl:,.2f}",
)


with st.expander(
    "View current positions"
):

    st.json(
        updated_portfolio.positions
    )

    st.markdown(
        "### Market Prices Used"
    )

    st.json(
        market_prices
    )


# ============================================================
# ADAPTATION
# ============================================================

st.markdown(
    '<div class="section">08 / ADAPTATION</div>',
    unsafe_allow_html=True,
)

if adaptation_feedback:

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Execution Outcome",
        adaptation_feedback.execution_outcome,
    )

    c2.metric(
        "Resulting Position",
        f"{adaptation_feedback.resulting_position:.0f}",
    )

    c3.metric(
        "Resulting P&L",
        f"₹{adaptation_feedback.pnl:,.2f}",
    )

    if reassessment:

        st.info(
            f"Next recommendation: "
            f"{reassessment.action} "
            f"with "
            f"{reassessment.confidence:.1%} confidence. "
            f"{reassessment.reason}"
        )

else:

    st.info(
        "No execution feedback was generated."
    )


# ============================================================
# VOICE
# ============================================================

st.markdown(
    '<div class="section">09 / VOICE INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

if st.button(
    "🎙️ Generate Voice Explanation"
):

    try:

        from backend.voice import VoiceExplainer

        explainer = VoiceExplainer()

        path = explainer.generate_audio(
            agent_decision
        )

        st.audio(
            path,
            format="audio/mp3",
        )

    except Exception as exc:

        st.warning(
            f"Voice unavailable: {exc}"
        )


# ============================================================
# DATA STATUS
# ============================================================

st.markdown(
    '<div class="section">10 / DATA STATUS</div>',
    unsafe_allow_html=True,
)

st.write(
    f"Last Updated: "
    f"{market_state.timestamp.strftime('%d %b %Y %H:%M:%S UTC')}"
)

st.write(
    f"Data Freshness: "
    f"{market_state.data_age_seconds:.1f} seconds"
)


# ============================================================
# DIAGNOSTICS
# ============================================================

with st.expander(
    "⌘ View complete diagnostics"
):

    st.write("Selected Asset")
    st.write(selected_asset)

    st.write("Market State")
    st.json(vars(market_state))

    st.write("Market Prices")
    st.json(market_prices)

    st.write("Portfolio Positions")
    st.json(
        portfolio_manager.positions
    )

    st.write("Agent Decision")
    st.json(vars(agent_decision))

    st.write("Risk Decision")
    st.json(vars(risk_decision))

    if execution_result:

        st.write("Execution Result")
        st.json(
            vars(execution_result)
        )

    st.write("Portfolio State")
    st.json(
        vars(updated_portfolio)
    )

