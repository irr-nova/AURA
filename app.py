import streamlit as st

from backend.market_data import MarketDataProvider
from backend.market_simulator import MarketSimulator


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AURA — Market Intelligence",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Market data
# ---------------------------------------------------------

@st.cache_resource
def get_market_provider():
    simulator = MarketSimulator()
    return MarketDataProvider(simulator)


provider = get_market_provider()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("AURA")
st.caption("Autonomous Unified Risk & Allocation — Market Intelligence")


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Market Intelligence")

selected_asset = st.sidebar.selectbox(
    "Select Asset",
    ["AAPL", "TSLA", "NVDA"],
)

if st.sidebar.button("Refresh Market Data"):
    st.rerun()


# ---------------------------------------------------------
# Get current market state
# ---------------------------------------------------------

market_state = provider.get_market_state(selected_asset)


# ---------------------------------------------------------
# Main metrics
# ---------------------------------------------------------

st.subheader(f"{market_state.asset} — Live Market State")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Price",
        f"${market_state.price:,.2f}",
    )

with col2:
    st.metric(
        "Volume",
        f"{market_state.volume:,.0f}",
    )

with col3:
    st.metric(
        "Liquidity",
        f"{market_state.liquidity:.2%}",
    )

with col4:
    st.metric(
        "Volatility",
        f"{market_state.volatility:.2%}",
    )


# ---------------------------------------------------------
# Market signals
# ---------------------------------------------------------

st.subheader("Market Signals")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Sentiment",
        f"{market_state.sentiment:.2f}",
    )

with col2:
    st.metric(
        "News Signal",
        f"{market_state.news_signal:.2f}",
    )

with col3:
    st.metric(
        "Market Regime",
        market_state.market_regime,
    )


# ---------------------------------------------------------
# Data freshness
# ---------------------------------------------------------

st.subheader("Data Status")

st.write(
    f"**Timestamp:** {market_state.timestamp.isoformat()}"
)

st.write(
    f"**Data age:** {market_state.data_age_seconds:.1f} seconds"
)


# ---------------------------------------------------------
# Raw MarketState
# ---------------------------------------------------------

with st.expander("View MarketState"):
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