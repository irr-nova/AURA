import streamlit as st

from backend.market_data import MarketDataProvider
from backend.market_simulator import MarketSimulator


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AURA — Market Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# MARKET DATA
# ============================================================

@st.cache_resource
def get_market_provider():
    simulator = MarketSimulator()
    return MarketDataProvider(simulator)


provider = get_market_provider()


# ============================================================
# CUSTOM CSS — BLACK + GOLD
# ============================================================

st.html(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

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

    .block-container {
        max-width: 1450px;
        padding-top: 3.5rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: #090909;
        border-right: 1px solid #292929;
    }

    .sidebar-logo {
        color: #D4AF37;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        margin-bottom: 0.25rem;
    }

    .sidebar-subtitle {
        color: #777777;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .sidebar-status {
        margin-top: 2rem;
        border-top: 1px solid #242424;
        padding-top: 1.5rem;
    }


    /* ========================================================
       STATUS
       ======================================================== */

    .status-label {
        color: #6E6E6E;
        font-size: 0.70rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 1rem;
        margin-bottom: 0.25rem;
    }

    .status-value {
        color: #D8D5CB;
        font-size: 0.90rem;
    }

    .online {
        color: #D4AF37;
    }


    /* ========================================================
       AURA HEADER
       ======================================================== */

    .aura-header {
        padding: 0.8rem 0 2rem 0;
        border-bottom: 1px solid #292929;
        margin-bottom: 2rem;
    }

    .aura-logo {
        color: #D4AF37;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        line-height: 1.15;
        padding-top: 0.15rem;
    }

    .aura-subtitle {
        margin-top: 0.6rem;
        color: #858585;
        font-size: 0.95rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }


    /* ========================================================
       SECTION LABELS
       ======================================================== */

    .section-label {
        color: #D4AF37;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-top: 1.8rem;
        margin-bottom: 0.55rem;
    }

    .section-title {
        color: #F1EFE7;
        font-size: 1.45rem;
        font-weight: 650;
        margin-bottom: 1.25rem;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    .metric-card {
        background: #0C0C0C;
        border: 1px solid #282828;
        border-radius: 4px;
        padding: 1.15rem 1.25rem;
        min-height: 125px;
        box-sizing: border-box;
    }

    .metric-card:hover {
        border-color: #80691D;
    }

    .metric-label {
        color: #777777;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.65rem;
    }

    .metric-value {
        color: #F2F0E8;
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.15;
    }

    .metric-gold {
        color: #D4AF37;
    }

    .metric-small {
        color: #666666;
        font-size: 0.75rem;
        margin-top: 0.45rem;
    }


    /* ========================================================
       MARKET REGIME
       ======================================================== */

    .regime {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        border-radius: 3px;
    }

    .regime-bull {
        border: 1px solid #80691D;
        background: #151208;
        color: #D4AF37;
    }

    .regime-bear {
        border: 1px solid #633232;
        background: #160909;
        color: #D87B7B;
    }

    .regime-sideways {
        border: 1px solid #555555;
        background: #111111;
        color: #B8B8B8;
    }

    .regime-high {
        border: 1px solid #80551D;
        background: #160F07;
        color: #D99B52;
    }


    /* ========================================================
       MAIN DATA STATUS
       ======================================================== */

    .status-card-main {
        background: #0A0A0A;
        border: 1px solid #242424;
        border-radius: 4px;
        padding: 1.1rem 1.25rem;
    }


    /* ========================================================
       AURA INTELLIGENCE
       ======================================================== */

    .intelligence-card {
        background: #0B0B0B;
        border: 1px solid #3B321A;
        border-left: 3px solid #D4AF37;
        padding: 1.35rem 1.5rem;
        margin-top: 1rem;
        border-radius: 3px;
    }

    .signal-title {
        color: #D4AF37;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .signal-text {
        color: #B9B7AE;
        font-size: 0.92rem;
        line-height: 1.65;
        margin-top: 0.65rem;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .aura-footer {
        margin-top: 3rem;
        padding-top: 1.25rem;
        border-top: 1px solid #252525;
        color: #555555;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-align: center;
    }

    </style>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-logo">AURA</div>

        <div class="sidebar-subtitle">
            Market Intelligence
        </div>
        """
    )

    selected_asset = st.selectbox(
        "Select Asset",
        ["AAPL", "TSLA", "NVDA"],
        key="asset_selector",
    )

    if st.button(
        "↻  Refresh Market Data",
        use_container_width=True,
        key="refresh_button",
    ):
        st.rerun()

    st.html(
        """
        <div class="sidebar-status">

            <div class="status-label">
                System Status
            </div>

            <div class="status-value">
                <span class="online">●</span> ONLINE
            </div>

            <div class="status-label">
                Data Source
            </div>

            <div class="status-value">
                MARKET SIMULATOR
            </div>

            <div class="status-label">
                Display Currency
            </div>

            <div class="status-value">
                INR
            </div>

        </div>
        """
    )


# ============================================================
# GET MARKET STATE
# ============================================================

market_state = provider.get_market_state(selected_asset)


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="aura-header">

        <div class="aura-logo">
            AURA
        </div>

        <div class="aura-subtitle">
            Autonomous Unified Risk & Allocation — Market Intelligence
        </div>

    </div>
    """
)


# ============================================================
# 01 / MARKET STATE
# ============================================================

st.html(
    """
    <div class="section-label">
        01 / Market State
    </div>
    """
)

st.html(
    f"""
    <div class="section-title">
        {market_state.asset} — Live Market State
    </div>
    """
)


col1, col2, col3, col4 = st.columns(4)


# ---------------- PRICE ----------------

with col1:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Price
            </div>

            <div class="metric-value metric-gold">
                ₹{market_state.price:,.2f}
            </div>

            <div class="metric-small">
                INR
            </div>

        </div>
        """
    )


# ---------------- VOLUME ----------------

with col2:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Volume
            </div>

            <div class="metric-value">
                {market_state.volume:,.0f}
            </div>

            <div class="metric-small">
                Units traded
            </div>

        </div>
        """
    )


# ---------------- LIQUIDITY ----------------

with col3:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Liquidity
            </div>

            <div class="metric-value">
                {market_state.liquidity:.2%}
            </div>

            <div class="metric-small">
                Market liquidity
            </div>

        </div>
        """
    )


# ---------------- VOLATILITY ----------------

with col4:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Volatility
            </div>

            <div class="metric-value">
                {market_state.volatility:.2%}
            </div>

            <div class="metric-small">
                Current volatility
            </div>

        </div>
        """
    )


# ============================================================
# 02 / MARKET SIGNALS
# ============================================================

st.html(
    """
    <div class="section-label">
        02 / Market Signals
    </div>
    """
)


# Sentiment description

if market_state.sentiment >= 0.3:
    sentiment_description = "Constructive"
elif market_state.sentiment > -0.3:
    sentiment_description = "Neutral"
else:
    sentiment_description = "Negative"


# News description

if market_state.news_signal >= 0.3:
    news_description = "Positive news signal"
elif market_state.news_signal > -0.3:
    news_description = "Neutral news signal"
else:
    news_description = "Negative news signal"


# Regime class

regime = market_state.market_regime

if regime == "BULL":
    regime_class = "regime-bull"
elif regime == "BEAR":
    regime_class = "regime-bear"
elif regime == "HIGH_VOLATILITY":
    regime_class = "regime-high"
else:
    regime_class = "regime-sideways"


col1, col2, col3 = st.columns(3)


# ---------------- SENTIMENT ----------------

with col1:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Sentiment
            </div>

            <div class="metric-value metric-gold">
                {market_state.sentiment:.2f}
            </div>

            <div class="metric-small">
                {sentiment_description}
            </div>

        </div>
        """
    )


# ---------------- NEWS SIGNAL ----------------

with col2:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                News Signal
            </div>

            <div class="metric-value metric-gold">
                {market_state.news_signal:.2f}
            </div>

            <div class="metric-small">
                {news_description}
            </div>

        </div>
        """
    )


# ---------------- MARKET REGIME ----------------

with col3:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Market Regime
            </div>

            <div style="margin-top:0.7rem;">

                <span class="regime {regime_class}">
                    {regime}
                </span>

            </div>

            <div class="metric-small">
                Current simulated regime
            </div>

        </div>
        """
    )


# ============================================================
# 03 / DATA STATUS
# ============================================================

st.html(
    """
    <div class="section-label">
        03 / Data Status
    </div>
    """
)

st.html(
    f"""
    <div class="status-card-main">

        <div class="status-label">
            Last Updated
        </div>

        <div class="status-value">
            {market_state.timestamp.strftime("%d %b %Y  •  %H:%M:%S UTC")}
        </div>

        <div class="status-label">
            Data Freshness
        </div>

        <div class="status-value">
            <span class="online">●</span>
            {market_state.data_age_seconds:.1f} seconds
        </div>

    </div>
    """
)


# ============================================================
# 04 / AURA INTELLIGENCE
# ============================================================

st.html(
    """
    <div class="section-label">
        04 / AURA Intelligence
    </div>
    """
)


if market_state.market_regime == "BULL":

    intelligence_text = (
        "Positive market conditions detected. "
        "Sentiment is constructive and the current simulated "
        "market regime is bullish."
    )

elif market_state.market_regime == "BEAR":

    intelligence_text = (
        "Defensive market conditions detected. "
        "Sentiment is negative and the current simulated "
        "market regime is bearish."
    )

elif market_state.market_regime == "HIGH_VOLATILITY":

    intelligence_text = (
        "Elevated market risk detected. "
        "Volatility is high and market conditions require "
        "additional caution."
    )

else:

    intelligence_text = (
        "Market conditions are relatively balanced. "
        "Signals indicate a sideways regime."
    )


st.html(
    f"""
    <div class="intelligence-card">

        <div class="signal-title">
            AURA MARKET SIGNAL
        </div>

        <div class="signal-text">
            {intelligence_text}
        </div>

    </div>
    """
)


# ============================================================
# RAW MARKET STATE
# ============================================================

with st.expander("⌄  View raw MarketState contract"):

    st.json(
        {
            "asset": market_state.asset,
            "price": market_state.price,
            "volume": market_state.volume,
            "liquidity": market_state.liquidity,
            "volatility": market_state.volatility,
            "sentiment": market_state.sentiment,
            "news_signal": market_state.news_signal,
            "market_regime": market_state.market_regime,
            "timestamp": market_state.timestamp.isoformat(),
            "data_age_seconds": market_state.data_age_seconds,
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="aura-footer">
        AURA • AUTONOMOUS UNIFIED RISK & ALLOCATION • MARKET INTELLIGENCE
    </div>
    """
)