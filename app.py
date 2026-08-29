from datetime import datetime, timezone
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from backend.market_data import MarketDataProvider
from backend.market_simulator import MarketSimulator
from backend.agent import AutonomousAgent
from backend.portfolio import PortfolioManager
from backend.risk_engine import RiskEngine
from backend.execution import ExecutionEngine
from backend.adaptation import AdaptationManager
from backend.contracts import ApprovedOrder


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AURA — Autonomous Market Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "aura logo.jpeg"


# ============================================================
# SERVICES
# ============================================================

@st.cache_resource
def get_market_provider():
    return MarketDataProvider(MarketSimulator())


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
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "aura_cycle": None,
    "voice_path": None,
    "aura_selected_asset": None,
    "market_history": [],
    "portfolio_history": [],
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background: #050505;
        color: #F2F0E8;
    }

    [data-testid="stAppViewContainer"] {
        background: #050505;
    }

    [data-testid="stHeader"] {
        background: #050505;
    }

    [data-testid="stSidebar"] {
        background: #090909;
    }

    [data-testid="stSidebarContent"] {
        background: #090909;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 3rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] h1 {
        color: #D4AF37 !important;
        letter-spacing: .12em;
    }


    /* ======================================================
       AURA BRAND
       ====================================================== */

    .brand-wrapper {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin-bottom: 0.25rem;
    }

    .brand-logo {
        width: 115px;
        height: 115px;
        object-fit: contain;
        border-radius: 10px;
        flex-shrink: 0;
    }

    .brand-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .aura-title {
        color: #D4AF37 !important;
        font-size: 3.25rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: .18em;
        margin: 0;
    }

    .tagline {
        color: #F2F0E8 !important;
        font-size: 1rem;
        font-weight: 500;
        letter-spacing: .12em;
        margin-top: .65rem;
    }

    .subtitle {
        color: #777777 !important;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-top: .4rem;
        margin-bottom: 2.2rem;
        font-size: .75rem;
    }


    /* ======================================================
       SECTIONS
       ====================================================== */

    .section {
        color: #D4AF37 !important;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .15em;
        margin-top: 2.2rem;
        margin-bottom: .9rem;
    }


    /* ======================================================
       MARKET CARDS
       ====================================================== */

    .card {
        background: #0C0C0C !important;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 1.25rem;
        min-height: 125px;
        box-sizing: border-box;
    }

    .label {
        color: #777777 !important;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
    }

    .value {
        color: #F2F0E8 !important;
        font-size: 1.7rem;
        font-weight: 700;
        margin-top: .55rem;
    }

    .gold {
        color: #D4AF37 !important;
    }

    .positive {
        color: #22C55E !important;
    }

    .negative {
        color: #EF4444 !important;
    }


    /* ======================================================
       CHART HEADERS
       ====================================================== */

    .chart-header {
        color: #F2F0E8;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: .3rem;
    }

    .chart-description {
        color: #777777;
        font-size: .78rem;
        margin-bottom: .8rem;
    }


    /* ======================================================
       PIPELINE
       ====================================================== */

    .pipeline-card {
        background: #0C0C0C;
        border: 1px solid #242424;
        border-radius: 8px;
        padding: 1rem;
        min-height: 105px;
    }

    .pipeline-label {
        color: #666666;
        font-size: .65rem;
        font-weight: 700;
        letter-spacing: .12em;
    }

    .pipeline-value {
        color: #F2F0E8;
        font-size: 1.05rem;
        font-weight: 800;
        margin-top: .45rem;
    }

    .pipeline-detail {
        color: #888888;
        font-size: .72rem;
        margin-top: .25rem;
    }


    /* ======================================================
       METRICS
       ====================================================== */

    [data-testid="stMetric"] {
        background: #0C0C0C;
        border: 1px solid #242424;
        border-radius: 8px;
        padding: 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #888888 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F2F0E8 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #888888 !important;
    }


    /* ======================================================
       EXPANDERS
       ====================================================== */

    [data-testid="stExpander"] {
        border-color: #282828 !important;
        background: #090909 !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        border-radius: 6px;
        border: 1px solid #333333;
        background: #111111;
        color: #F2F0E8;
    }

    .stButton > button:hover {
        border-color: #D4AF37;
        color: #D4AF37;
    }


    /* ======================================================
       DATAFRAME
       ====================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid #242424;
        border-radius: 8px;
    }


    /* ======================================================
       DIVIDERS
       ====================================================== */

    hr {
        border-color: #242424 !important;
    }


    /* ======================================================
       INFO / SUCCESS / WARNING
       ====================================================== */

    [data-testid="stAlert"] {
        border-radius: 7px;
    }


    /* ======================================================
       MOBILE
       ====================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .brand-logo {
            width: 85px;
            height: 85px;
        }

        .aura-title {
            font-size: 2.2rem;
        }

        .tagline {
            font-size: .72rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# AURA")

    st.caption(
        "AUTONOMOUS MARKET INTELLIGENCE"
    )

    selected_asset = st.selectbox(
        "Select Asset",
        ["AAPL", "TSLA", "NVDA"],
        key="asset_selector",
    )

    initial_cash = st.number_input(
        "Portfolio Capital",
        min_value=1000.0,
        max_value=10_000_000.0,
        value=100_000.0,
        step=1000.0,
    )

    st.markdown("")

    if st.button(
        "↻ Refresh Market Data",
        use_container_width=True,
    ):

        st.session_state.aura_cycle = None
        st.session_state.voice_path = None

        st.rerun()

    if st.button(
        "Reset Portfolio",
        use_container_width=True,
    ):

        st.session_state.pop(
            "portfolio_manager",
            None,
        )

        st.session_state.pop(
            "portfolio_initial_cash",
            None,
        )

        st.session_state.aura_cycle = None
        st.session_state.voice_path = None
        st.session_state.market_history = []
        st.session_state.portfolio_history = []

        st.rerun()

    st.markdown("---")

    st.markdown("**SYSTEM STATUS**")

    st.success("● ONLINE")

    st.caption("Pipeline: AUTONOMOUS")
    st.caption("Data Source: MARKET SIMULATOR")
    st.caption("Currency: INR")


# ============================================================
# PORTFOLIO
# ============================================================

if (
    "portfolio_manager" not in st.session_state
    or st.session_state.get(
        "portfolio_initial_cash"
    ) != initial_cash
):

    st.session_state["portfolio_manager"] = (
        PortfolioManager(
            initial_cash=initial_cash
        )
    )

    st.session_state["portfolio_initial_cash"] = (
        initial_cash
    )

    st.session_state.aura_cycle = None
    st.session_state.voice_path = None


portfolio_manager = (
    st.session_state["portfolio_manager"]
)


# ============================================================
# MARKET HELPERS
# ============================================================

def safe_get_market_state(asset):

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

    if selected_state is not None:

        prices[selected_asset] = float(
            selected_state.price
        )

    positions = getattr(
        portfolio,
        "_positions",
        {},
    ) or {}

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

        state = safe_get_market_state(asset)

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

    positions = getattr(
        portfolio,
        "_positions",
        {},
    ) or {}

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
# ASSET CHANGE DETECTION
# ============================================================

previous_asset = st.session_state.get(
    "aura_selected_asset"
)

if previous_asset != selected_asset:

    st.session_state[
        "aura_selected_asset"
    ] = selected_asset

    st.session_state.aura_cycle = None
    st.session_state.voice_path = None
    st.session_state.market_history = []


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

    st.stop()


# ============================================================
# AUTONOMOUS CYCLE
# ============================================================

if st.session_state.aura_cycle is None:

    # --------------------------------------------------------
    # AGENT
    # --------------------------------------------------------

    agent_decision = agent.decide(
        market_state,
        portfolio_state,
    )

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk_decision = risk_engine.evaluate(
        agent_decision,
        market_state,
        portfolio_state,
    )

    execution_result = None
    execution_error = None
    adaptation_feedback = None
    reassessment = None

    updated_portfolio = portfolio_state

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    if (
        risk_decision.status
        in {"APPROVE", "MODIFY"}
        and risk_decision.approved_quantity > 0
        and agent_decision.action
        in {"BUY", "SELL", "REDUCE"}
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

            # ------------------------------------------------
            # UPDATE PORTFOLIO
            # ------------------------------------------------

            updated_portfolio = (
                portfolio_manager.update(
                    execution_result,
                    market_prices,
                )
            )

            # ------------------------------------------------
            # REBUILD PRICES
            # ------------------------------------------------

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

            # ------------------------------------------------
            # FINAL VALUATION
            # ------------------------------------------------

            updated_portfolio = (
                portfolio_manager.get_state(
                    final_market_prices
                )
            )

            market_prices = final_market_prices

            # ------------------------------------------------
            # ADAPTATION
            # ------------------------------------------------

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

            # ------------------------------------------------
            # REASSESSMENT
            # ------------------------------------------------

            reassessment = agent.decide(
                market_state,
                updated_portfolio,
            )

        except Exception as exc:

            execution_error = str(exc)

    # --------------------------------------------------------
    # SAVE COMPLETE CYCLE
    # --------------------------------------------------------

    st.session_state.aura_cycle = {

        "market_state": market_state,

        "agent_decision": agent_decision,

        "risk_decision": risk_decision,

        "execution_result": execution_result,

        "execution_error": execution_error,

        "updated_portfolio": updated_portfolio,

        "adaptation_feedback": (
            adaptation_feedback
        ),

        "reassessment": reassessment,

        "market_prices": market_prices,
    }

else:

    cycle = st.session_state.aura_cycle

    market_state = cycle[
        "market_state"
    ]

    agent_decision = cycle[
        "agent_decision"
    ]

    risk_decision = cycle[
        "risk_decision"
    ]

    execution_result = cycle[
        "execution_result"
    ]

    execution_error = cycle[
        "execution_error"
    ]

    updated_portfolio = cycle[
        "updated_portfolio"
    ]

    adaptation_feedback = cycle[
        "adaptation_feedback"
    ]

    reassessment = cycle[
        "reassessment"
    ]

    market_prices = cycle[
        "market_prices"
    ]


# ============================================================
# RECORD HISTORY
# ============================================================

history_timestamp = (
    market_state.timestamp.strftime(
        "%H:%M:%S"
    )
)

market_history = (
    st.session_state.market_history
)

history_entry = {
    "time": history_timestamp,
    "price": float(
        market_state.price
    ),
    "sentiment": float(
        market_state.sentiment
    ),
    "news_signal": float(
        market_state.news_signal
    ),
    "liquidity": float(
        market_state.liquidity
    ),
    "volatility": float(
        market_state.volatility
    ),
    "risk_score": float(
        risk_decision.risk_score
    ),
}


if not market_history:

    market_history.append(
        history_entry
    )

elif (
    market_history[-1]["time"]
    != history_entry["time"]
):

    market_history.append(
        history_entry
    )


if len(market_history) > 100:

    del market_history[:-100]


# ============================================================
# PORTFOLIO HISTORY
# ============================================================

portfolio_history = (
    st.session_state.portfolio_history
)

portfolio_entry = {
    "time": history_timestamp,
    "value": float(
        updated_portfolio.total_value
    ),
    "pnl": float(
        updated_portfolio.pnl
    ),
}


if not portfolio_history:

    portfolio_history.append(
        portfolio_entry
    )

elif (
    portfolio_history[-1]["time"]
    != portfolio_entry["time"]
):

    portfolio_history.append(
        portfolio_entry
    )


if len(portfolio_history) > 100:

    del portfolio_history[:-100]


# ============================================================
# HEADER
# ============================================================

if LOGO_PATH.exists():

    logo_html = (
        f'<img class="brand-logo" '
        f'src="data:image/jpeg;base64,'
    )

    import base64

    with open(
        LOGO_PATH,
        "rb",
    ) as logo_file:

        encoded_logo = (
            base64.b64encode(
                logo_file.read()
            ).decode()
        )

    logo_html += (
        encoded_logo
        + '" alt="AURA Logo">'
    )

else:

    logo_html = (
        '<div class="brand-logo"></div>'
    )


st.markdown(
    f"""
    <div class="brand-wrapper">
        {logo_html}
        <div class="brand-text">
            <div class="aura-title">AURA</div>
            <div class="tagline">
                Where Intelligence Meets the Market
            </div>
        </div>
    </div>
    <div class="subtitle">
        Autonomous Unified Risk & Allocation —
        Market Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 01 / MARKET STATE
# ============================================================

st.markdown(
    '<div class="section">'
    '01 / MARKET STATE'
    '</div>',
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
# 02 / MARKET ANALYTICS
# ============================================================

st.markdown(
    '<div class="section">'
    '02 / MARKET ANALYTICS'
    '</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)


# ============================================================
# PRICE CHART
# ============================================================

with chart_col1:

    st.markdown(
        '<div class="chart-header">'
        'Price Movement'
        '</div>'
        '<div class="chart-description">'
        'Short-term price movement for the selected asset.'
        '</div>',
        unsafe_allow_html=True,
    )

    if len(market_history) >= 2:

        price_df = pd.DataFrame(
            market_history
        )

        price_min = float(
            price_df["price"].min()
        )

        price_max = float(
            price_df["price"].max()
        )

        price_range = (
            price_max - price_min
        )

        if price_range <= 0:

            padding = max(
                price_max * 0.002,
                0.01,
            )

        else:

            padding = (
                price_range * 0.15
            )

        first_price = float(
            price_df["price"].iloc[0]
        )

        latest_price = float(
            price_df["price"].iloc[-1]
        )

        movement_up = (
            latest_price >= first_price
        )

        movement_color = (
            "#22C55E"
            if movement_up
            else "#EF4444"
        )

        movement_label = (
            "▲"
            if movement_up
            else "▼"
        )

        movement_change = (
            latest_price - first_price
        )

        if first_price != 0:

            movement_pct = (
                movement_change
                / first_price
            ) * 100

        else:

            movement_pct = 0.0

        st.caption(
            f"Range: ₹{price_min:,.2f} — "
            f"₹{price_max:,.2f} · "
            f"Move: {movement_label} "
            f"₹{movement_change:+,.2f} "
            f"({movement_pct:+.2f}%)"
        )

        price_chart = (
            alt.Chart(price_df)
            .mark_line(
                strokeWidth=2.5,
                color=movement_color,
            )
            .encode(
                x=alt.X(
                    "time:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelColor="#777777",
                        grid=False,
                    ),
                ),
                y=alt.Y(
                    "price:Q",
                    title="Price (₹)",
                    scale=alt.Scale(
                        domain=[
                            price_min - padding,
                            price_max + padding,
                        ],
                        zero=False,
                    ),
                    axis=alt.Axis(
                        labelColor="#777777",
                        titleColor="#777777",
                        gridColor="#202020",
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        "time:N",
                        title="Time",
                    ),
                    alt.Tooltip(
                        "price:Q",
                        title="Price",
                        format=",.2f",
                    ),
                ],
            )
            .properties(
                height=320
            )
        )

        st.altair_chart(
            price_chart,
            use_container_width=True,
        )

    else:

        st.info(
            "Collecting price observations..."
        )


# ============================================================
# MARKET SIGNAL CHART
# ============================================================

with chart_col2:

    st.markdown(
        '<div class="chart-header">'
        'Market Signals'
        '</div>'
        '<div class="chart-description">'
        'Sentiment and news strength driving the agent.'
        '</div>',
        unsafe_allow_html=True,
    )

    if market_history:

        signal_df = pd.DataFrame(
            market_history
        )

        signal_long = signal_df.melt(
            id_vars=["time"],
            value_vars=[
                "sentiment",
                "news_signal",
            ],
            var_name="Signal",
            value_name="Value",
        )

        signal_long["Signal"] = (
            signal_long["Signal"].map(
                {
                    "sentiment": "Sentiment",
                    "news_signal": "News Signal",
                }
            )
        )

        signal_chart = (
            alt.Chart(signal_long)
            .mark_line(
                strokeWidth=2,
            )
            .encode(
                x=alt.X(
                    "time:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelColor="#777777",
                        grid=False,
                    ),
                ),
                y=alt.Y(
                    "Value:Q",
                    title="Signal",
                    scale=alt.Scale(
                        domain=[0, 1]
                    ),
                    axis=alt.Axis(
                        labelColor="#777777",
                        titleColor="#777777",
                        gridColor="#202020",
                    ),
                ),
                color=alt.Color(
                    "Signal:N",
                    scale=alt.Scale(
                        domain=[
                            "Sentiment",
                            "News Signal",
                        ],
                        range=[
                            "#22C55E",
                            "#D4AF37",
                        ],
                    ),
                    legend=alt.Legend(
                        title=None,
                        labelColor="#AAAAAA",
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        "time:N",
                        title="Time",
                    ),
                    alt.Tooltip(
                        "Signal:N"
                    ),
                    alt.Tooltip(
                        "Value:Q",
                        format=".2f",
                    ),
                ],
            )
            .properties(
                height=320
            )
        )

        st.altair_chart(
            signal_chart,
            use_container_width=True,
        )

    else:

        st.info(
            "Signal history will appear as "
            "market cycles are refreshed."
        )


# ============================================================
# 03 / MARKET SIGNALS
# ============================================================

st.markdown(
    '<div class="section">'
    '03 / MARKET SIGNALS'
    '</div>',
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
# 04 / AUTONOMOUS PIPELINE
# ============================================================

st.markdown(
    '<div class="section">'
    '04 / AUTONOMOUS PIPELINE'
    '</div>',
    unsafe_allow_html=True,
)

pipeline_data = [
    (
        "MARKET",
        "LIVE",
        market_state.asset,
    ),
    (
        "AGENT",
        agent_decision.action,
        f"{agent_decision.confidence:.1%}",
    ),
    (
        "RISK",
        risk_decision.status,
        f"{risk_decision.risk_score:.2f}",
    ),
    (
        "EXECUTION",
        (
            execution_result.status
            if execution_result
            else "SKIPPED"
        ),
        "",
    ),
    (
        "PORTFOLIO",
        (
            "UPDATED"
            if execution_result
            else "UNCHANGED"
        ),
        f"₹{updated_portfolio.total_value:,.0f}",
    ),
    (
        "ADAPTATION",
        (
            "COMPLETE"
            if adaptation_feedback
            else "WAITING"
        ),
        "",
    ),
]

pipeline = st.columns(6)

for column, data in zip(
    pipeline,
    pipeline_data,
):

    label, value, detail = data

    with column:

        value_class = ""

        if value in {
            "BUY",
            "APPROVE",
            "FILLED",
            "COMPLETE",
            "LIVE",
            "UPDATED",
        }:

            value_class = "positive"

        elif value in {
            "SELL",
            "REJECT",
            "FAILED",
        }:

            value_class = "negative"

        st.markdown(
            f"""
            <div class="pipeline-card">
                <div class="pipeline-label">
                    {label}
                </div>
                <div class="pipeline-value {value_class}">
                    {value}
                </div>
                <div class="pipeline-detail">
                    {detail}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 05 / AGENT DECISION
# ============================================================

st.markdown(
    '<div class="section">'
    '05 / AGENT DECISION'
    '</div>',
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
# 06 / RISK ENGINE
# ============================================================

st.markdown(
    '<div class="section">'
    '06 / RISK ENGINE'
    '</div>',
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

    st.markdown(
        '<div class="chart-header">'
        'Risk Factors'
        '</div>',
        unsafe_allow_html=True,
    )

    for factor in (
        risk_decision.risk_factors
    ):

        st.caption(
            f"• {factor}"
        )


# ============================================================
# 07 / RISK & MARKET PROFILE
# ============================================================

st.markdown(
    '<div class="section">'
    '07 / RISK & MARKET PROFILE'
    '</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)


# ============================================================
# MARKET PROFILE
# ============================================================

with chart_col1:

    st.markdown(
        '<div class="chart-header">'
        'Current Market Profile'
        '</div>'
        '<div class="chart-description">'
        'Normalized indicators used by the autonomous pipeline.'
        '</div>',
        unsafe_allow_html=True,
    )

    profile_df = pd.DataFrame(
        {
            "Indicator": [
                "Sentiment",
                "News Signal",
                "Liquidity",
                "Volatility",
            ],
            "Value": [
                float(
                    market_state.sentiment
                ),
                float(
                    market_state.news_signal
                ),
                float(
                    market_state.liquidity
                ),
                float(
                    market_state.volatility
                ),
            ],
        }
    )

    profile_chart = (
        alt.Chart(profile_df)
        .mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        )
        .encode(
            x=alt.X(
                "Indicator:N",
                title=None,
                axis=alt.Axis(
                    labelColor="#777777"
                ),
            ),
            y=alt.Y(
                "Value:Q",
                title=None,
                scale=alt.Scale(
                    domain=[0, 1]
                ),
                axis=alt.Axis(
                    labelColor="#777777",
                    gridColor="#202020",
                ),
            ),
            color=alt.Color(
                "Indicator:N",
                scale=alt.Scale(
                    domain=[
                        "Sentiment",
                        "News Signal",
                        "Liquidity",
                        "Volatility",
                    ],
                    range=[
                        "#22C55E",
                        "#D4AF37",
                        "#3B82F6",
                        "#EF4444",
                    ],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip(
                    "Indicator:N"
                ),
                alt.Tooltip(
                    "Value:Q",
                    format=".2f",
                ),
            ],
        )
        .properties(
            height=320
        )
    )

    st.altair_chart(
        profile_chart,
        use_container_width=True,
    )


# ============================================================
# RISK HISTORY
# ============================================================

with chart_col2:

    st.markdown(
        '<div class="chart-header">'
        'Risk Score History'
        '</div>'
        '<div class="chart-description">'
        'Risk score observed across autonomous cycles.'
        '</div>',
        unsafe_allow_html=True,
    )

    if market_history:

        risk_df = pd.DataFrame(
            market_history
        )

        risk_chart = (
            alt.Chart(risk_df)
            .mark_line(
                color="#EF4444",
                strokeWidth=2.5,
            )
            .encode(
                x=alt.X(
                    "time:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelColor="#777777",
                        grid=False,
                    ),
                ),
                y=alt.Y(
                    "risk_score:Q",
                    title="Risk",
                    scale=alt.Scale(
                        domain=[0, 1]
                    ),
                    axis=alt.Axis(
                        labelColor="#777777",
                        titleColor="#777777",
                        gridColor="#202020",
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        "time:N",
                        title="Time",
                    ),
                    alt.Tooltip(
                        "risk_score:Q",
                        title="Risk Score",
                        format=".3f",
                    ),
                ],
            )
            .properties(
                height=320
            )
        )

        st.altair_chart(
            risk_chart,
            use_container_width=True,
        )

    else:

        st.info(
            "Risk history will appear as "
            "new cycles are generated."
        )


# ============================================================
# 08 / EXECUTION
# ============================================================

st.markdown(
    '<div class="section">'
    '08 / EXECUTION'
    '</div>',
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
# 09 / PORTFOLIO STATE
# ============================================================

st.markdown(
    '<div class="section">'
    '09 / PORTFOLIO STATE'
    '</div>',
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

pnl_value = float(
    updated_portfolio.pnl
)

c4.metric(
    "P&L",
    f"₹{pnl_value:,.2f}",
)


# ============================================================
# PORTFOLIO CHARTS
# ============================================================

portfolio_chart_col1, portfolio_chart_col2 = (
    st.columns(2)
)


# ============================================================
# PORTFOLIO VALUE
# ============================================================

with portfolio_chart_col1:

    st.markdown(
        '<div class="chart-header">'
        'Portfolio Value'
        '</div>'
        '<div class="chart-description">'
        'Portfolio value across recorded AURA cycles.'
        '</div>',
        unsafe_allow_html=True,
    )

    if portfolio_history:

        portfolio_df = pd.DataFrame(
            portfolio_history
        )

        first_value = float(
            portfolio_df["value"].iloc[0]
        )

        last_value = float(
            portfolio_df["value"].iloc[-1]
        )

        portfolio_up = (
            last_value >= first_value
        )

        portfolio_color = (
            "#22C55E"
            if portfolio_up
            else "#EF4444"
        )

        portfolio_chart = (
            alt.Chart(portfolio_df)
            .mark_line(
                color=portfolio_color,
                strokeWidth=2.5,
            )
            .encode(
                x=alt.X(
                    "time:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelColor="#777777",
                        grid=False,
                    ),
                ),
                y=alt.Y(
                    "value:Q",
                    title="Portfolio Value (₹)",
                    scale=alt.Scale(
                        zero=False
                    ),
                    axis=alt.Axis(
                        labelColor="#777777",
                        titleColor="#777777",
                        gridColor="#202020",
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        "time:N",
                        title="Time",
                    ),
                    alt.Tooltip(
                        "value:Q",
                        title="Portfolio Value",
                        format=",.2f",
                    ),
                ],
            )
            .properties(
                height=320
            )
        )

        st.altair_chart(
            portfolio_chart,
            use_container_width=True,
        )

    else:

        st.info(
            "Portfolio history will appear "
            "after additional cycles."
        )


# ============================================================
# PORTFOLIO P&L
# ============================================================

with portfolio_chart_col2:

    st.markdown(
        '<div class="chart-header">'
        'Portfolio P&L'
        '</div>'
        '<div class="chart-description">'
        'Profit and loss across recorded cycles.'
        '</div>',
        unsafe_allow_html=True,
    )

    if portfolio_history:

        pnl_df = pd.DataFrame(
            portfolio_history
        )

        pnl_chart = (
            alt.Chart(pnl_df)
            .mark_line(
                strokeWidth=2.5,
            )
            .encode(
                x=alt.X(
                    "time:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelColor="#777777",
                        grid=False,
                    ),
                ),
                y=alt.Y(
                    "pnl:Q",
                    title="P&L (₹)",
                    scale=alt.Scale(
                        zero=False
                    ),
                    axis=alt.Axis(
                        labelColor="#777777",
                        titleColor="#777777",
                        gridColor="#202020",
                    ),
                ),
                color=alt.condition(
                    "datum.pnl >= 0",
                    alt.value("#22C55E"),
                    alt.value("#EF4444"),
                ),
                tooltip=[
                    alt.Tooltip(
                        "time:N",
                        title="Time",
                    ),
                    alt.Tooltip(
                        "pnl:Q",
                        title="P&L",
                        format=",.2f",
                    ),
                ],
            )
            .properties(
                height=320
            )
        )

        st.altair_chart(
            pnl_chart,
            use_container_width=True,
        )

    else:

        st.info(
            "P&L history will appear "
            "after additional cycles."
        )


# ============================================================
# CURRENT POSITIONS
# ============================================================

st.markdown(
    '<div class="chart-header">'
    'Current Positions'
    '</div>',
    unsafe_allow_html=True,
)

positions = (
    updated_portfolio.positions
)

if positions:

    position_rows = []

    for asset, quantity in positions.items():

        try:
            quantity = float(quantity)

        except (TypeError, ValueError):
            continue

        if quantity == 0:
            continue

        current_price = (
            market_prices.get(
                asset.upper()
            )
        )

        market_value = (
            quantity * current_price
            if current_price is not None
            else None
        )

        position_rows.append(
            {
                "Asset": asset.upper(),
                "Quantity": quantity,
                "Price": current_price,
                "Market Value": market_value,
            }
        )

    if position_rows:

        positions_df = pd.DataFrame(
            position_rows
        )

        st.dataframe(
            positions_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Quantity": (
                    st.column_config.NumberColumn(
                        format="%.2f"
                    )
                ),
                "Price": (
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    )
                ),
                "Market Value": (
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    )
                ),
            },
        )

    else:

        st.caption(
            "No active positions."
        )

else:

    st.caption(
        "No active positions."
    )


# ============================================================
# 10 / ADAPTATION
# ============================================================

st.markdown(
    '<div class="section">'
    '10 / ADAPTATION'
    '</div>',
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
            f"{reassessment.confidence:.1%} "
            f"confidence. "
            f"{reassessment.reason}"
        )

else:

    st.info(
        "No execution feedback was generated."
    )


# ============================================================
# 11 / VOICE INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section">'
    '11 / VOICE INTELLIGENCE'
    '</div>',
    unsafe_allow_html=True,
)


if st.button(
    "🎙️ Generate Voice Explanation"
):

    try:

        from backend.voice import VoiceExplainer

        explainer = VoiceExplainer()

        st.session_state.voice_path = (
            explainer.generate_audio(
                agent_decision
            )
        )

    except Exception as exc:

        st.session_state.voice_path = None

        st.warning(
            f"Voice unavailable: {exc}"
        )


if st.session_state.voice_path:

    st.audio(
        st.session_state.voice_path,
        format="audio/mp3",
    )


# ============================================================
# 12 / DATA STATUS
# ============================================================

st.markdown(
    '<div class="section">'
    '12 / DATA STATUS'
    '</div>',
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
# DEVELOPER DIAGNOSTICS
# ============================================================

with st.expander(
    "⌘ Developer diagnostics"
):

    st.caption(
        "Developer diagnostics only. "
        "This section contains the internal "
        "state used by the AURA pipeline."
    )

    # --------------------------------------------------------
    # MARKET STATE
    # --------------------------------------------------------

    st.markdown("### Market State")

    market_cols = st.columns(4)

    market_cols[0].metric(
        "Asset",
        market_state.asset,
    )

    market_cols[1].metric(
        "Price",
        f"₹{market_state.price:,.2f}",
    )

    market_cols[2].metric(
        "Regime",
        market_state.market_regime,
    )

    market_cols[3].metric(
        "Volatility",
        f"{market_state.volatility:.2%}",
    )

    # --------------------------------------------------------
    # MARKET SIGNALS
    # --------------------------------------------------------

    st.markdown("### Market Signals")

    signal_cols = st.columns(4)

    signal_cols[0].metric(
        "Sentiment",
        f"{market_state.sentiment:.3f}",
    )

    signal_cols[1].metric(
        "News Signal",
        f"{market_state.news_signal:.3f}",
    )

    signal_cols[2].metric(
        "Liquidity",
        f"{market_state.liquidity:.2%}",
    )

    signal_cols[3].metric(
        "Volume",
        f"{market_state.volume:,.0f}",
    )

    # --------------------------------------------------------
    # AGENT
    # --------------------------------------------------------

    st.markdown("### Agent")

    agent_cols = st.columns(4)

    agent_cols[0].metric(
        "Action",
        agent_decision.action,
    )

    agent_cols[1].metric(
        "Confidence",
        f"{agent_decision.confidence:.1%}",
    )

    agent_cols[2].metric(
        "Requested Qty",
        f"{agent_decision.requested_quantity:.0f}",
    )

    agent_cols[3].metric(
        "Expected Return",
        f"{agent_decision.expected_return:.2f}",
    )

    st.caption(
        f"Reason: {agent_decision.reason}"
    )

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    st.markdown("### Risk")

    risk_cols = st.columns(4)

    risk_cols[0].metric(
        "Status",
        risk_decision.status,
    )

    risk_cols[1].metric(
        "Risk Score",
        f"{risk_decision.risk_score:.3f}",
    )

    risk_cols[2].metric(
        "Approved Qty",
        f"{risk_decision.approved_quantity:.0f}",
    )

    risk_cols[3].metric(
        "Approved Amount",
        f"₹{risk_decision.approved_amount:,.2f}",
    )

    if risk_decision.risk_factors:

        st.caption(
            "Risk Factors"
        )

        for factor in (
            risk_decision.risk_factors
        ):

            st.write(
                f"• {factor}"
            )

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    st.markdown("### Execution")

    if execution_result:

        execution_cols = st.columns(4)

        execution_cols[0].metric(
            "Status",
            execution_result.status,
        )

        execution_cols[1].metric(
            "Quantity",
            f"{execution_result.executed_quantity:.0f}",
        )

        execution_cols[2].metric(
            "Price",
            f"₹{execution_result.executed_price:,.2f}",
        )

        execution_cols[3].metric(
            "Transaction Cost",
            f"₹{execution_result.transaction_cost:,.2f}",
        )

        if hasattr(
            execution_result,
            "slippage",
        ):

            st.caption(
                f"Slippage: "
                f"₹{execution_result.slippage:,.4f}"
            )

    else:

        st.caption(
            "No execution result."
        )

    # --------------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------------

    st.markdown("### Portfolio")

    portfolio_cols = st.columns(4)

    portfolio_cols[0].metric(
        "Portfolio Value",
        f"₹{updated_portfolio.total_value:,.2f}",
    )

    portfolio_cols[1].metric(
        "Cash",
        f"₹{updated_portfolio.available_cash:,.2f}",
    )

    portfolio_cols[2].metric(
        "Exposure",
        f"{updated_portfolio.current_exposure:.2%}",
    )

    portfolio_cols[3].metric(
        "P&L",
        f"₹{updated_portfolio.pnl:,.2f}",
    )

    # --------------------------------------------------------
    # POSITIONS
    # --------------------------------------------------------

    st.markdown("### Positions")

    if updated_portfolio.positions:

        diagnostic_positions = []

        for asset, quantity in (
            updated_portfolio.positions.items()
        ):

            current_price = (
                market_prices.get(
                    asset.upper()
                )
            )

            diagnostic_positions.append(
                {
                    "Asset": asset.upper(),
                    "Quantity": float(
                        quantity
                    ),
                    "Market Price": (
                        float(
                            current_price
                        )
                        if current_price
                        is not None
                        else None
                    ),
                    "Market Value": (
                        float(quantity)
                        * float(current_price)
                        if current_price
                        is not None
                        else None
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(
                diagnostic_positions
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Quantity": (
                    st.column_config.NumberColumn(
                        format="%.4f"
                    )
                ),
                "Market Price": (
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    )
                ),
                "Market Value": (
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    )
                ),
            },
        )

    else:

        st.caption(
            "No positions."
        )

    # --------------------------------------------------------
    # MARKET PRICE MAP
    # --------------------------------------------------------

    st.markdown(
        "### Market Price Map"
    )

    price_rows = [
        {
            "Asset": asset,
            "Price": price,
        }
        for asset, price
        in market_prices.items()
    ]

    if price_rows:

        st.dataframe(
            pd.DataFrame(
                price_rows
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price": (
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    )
                )
            },
        )

    else:

        st.caption(
            "No market prices available."
        )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    st.markdown("### History")

    history_cols = st.columns(2)

    with history_cols[0]:

        st.caption(
            f"Market observations: "
            f"{len(st.session_state.market_history)}"
        )

        if st.session_state.market_history:

            history_df = pd.DataFrame(
                st.session_state.market_history
            )

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.caption(
                "No market observations."
            )

    with history_cols[1]:

        st.caption(
            f"Portfolio observations: "
            f"{len(st.session_state.portfolio_history)}"
        )

        if st.session_state.portfolio_history:

            portfolio_history_df = (
                pd.DataFrame(
                    st.session_state.portfolio_history
                )
            )

            st.dataframe(
                portfolio_history_df,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.caption(
                "No portfolio observations."
            )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    st.markdown("### Timestamps")

    timestamp_cols = st.columns(3)

    timestamp_cols[0].caption(
        f"Market: {market_state.timestamp}"
    )

    timestamp_cols[1].caption(
        f"Agent: {agent_decision.timestamp}"
    )

    timestamp_cols[2].caption(
        f"Risk: {risk_decision.timestamp}"
    )