import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Junior Desk: Narrative Builder")

# --- 1. THE NARRATIVE DATA ENGINE ---
@st.cache_data(ttl=3600)
def fetch_terminal_v4():
    # Tracking DXY, US 10Y, and Proxies for Economic Surprise (Citi ESI is hard to get, so we use Momentum of Growth)
    tickers = {
        "DXY": "DX-Y.NYB",
        "US_10Y": "^TNX",
        "EEM": "EEM",           # Emerging Markets (Global Growth Sentiment)
        "Copper": "HG=F",
        "Gold": "GC=F",
        "VIX": "^VIX",
        "EURUSD": "EURUSD=X"
    }
    data = yf.download(list(tickers.values()), period="1y", interval="1d")['Close']
    return data.rename(columns={v: k for k, v in tickers.items()})

df = fetch_terminal_v4()

# --- 2. CALCULATING THE "SURPRISE" PROXY ---
# Institutional ESI measures Actual vs. Forecast. 
# For this dashboard, we use 10-day Price Momentum vs. 50-day Trend as a "Surprise Proxy"
df['Growth_Surprise'] = (df['US_10Y'] - df['US_10Y'].rolling(20).mean()) / df['US_10Y'].rolling(20).std()
df['Risk_Ratio'] = df['Copper'] / df['Gold']

# --- 3. DASHBOARD UI ---
st.title("🏛️ USD Weekly Narrative Builder")
st.markdown("### Goal: Construct the 'Why' behind the move.")

# ROW 1: THE CORE THEMES
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Dollar Strength (DXY)", f"{df['DXY'].iloc[-1]:.2f}")
    st.caption("The Scoreboard: Is the Dollar winning?")
with c2:
    st.metric("Growth Surprise Proxy", f"{df['Growth_Surprise'].iloc[-1]:.2f}σ")
    st.caption("The Engine: Are yields 'surprising' to the upside?")
with c3:
    st.metric("Global Risk Ratio", f"{df['Risk_Ratio'].iloc[-1]:.4f}")
    st.caption("The Vibe: Is the world building (Copper) or hiding (Gold)?")

st.divider()

# ROW 2: NARRATIVE VISUALIZATION
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 The Divergence: DXY vs. Growth Surprise")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index[-60:], y=df['DXY'].tail(60), name="DXY (Price)", yaxis="y1"))
    fig.add_trace(go.Bar(x=df.index[-60:], y=df['Growth_Surprise'].tail(60), name="Growth Surprise", yaxis="y2", opacity=0.3))
    
    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(title="DXY Price"),
        yaxis2=dict(title="Surprise (Sigma)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.info("**Storytelling Workshop:**")
    last_surprise = df['Growth_Surprise'].iloc[-1]
    last_dxy = (df['DXY'].iloc[-1] - df['DXY'].iloc[-5])
    
    if last_surprise > 1 and last_dxy > 0:
        st.success("📝 **Current Story:** 'US Exceptionalism'. Data is beating expectations and the Dollar is being rewarded. This is a healthy trend.")
    elif last_surprise < -1 and last_dxy > 0:
        st.error("📝 **Current Story:** 'Flight to Safety'. Data is missing expectations but the Dollar is RISING anyway. This means people are scared. Avoid risk assets.")
    elif last_surprise > 1 and last_dxy < 0:
        st.warning("📝 **Current Story:** 'Exhaustion'. Data is great but the Dollar is falling. The 'Good News' is already priced in. Watch for a reversal.")
    else:
        st.write("Neutral Narrative. Market is waiting for the next major catalyst (NFP/CPI).")

st.divider()

# ROW 3: THE JUNIOR DESK "BEYOND BLOOMBERG" CHECKLIST
st.subheader("📝 Monday Morning Narrative Assignment")
st.markdown("""
1. **The Divergence:** Did the Dollar move *opposite* to the Growth Surprise this week? If so, why? (e.g. Geopolitics, Month-end flows).
2. **The Laggard:** Look at **EURUSD**. If the US Growth Surprise is high but EURUSD isn't falling, is the ECB about to turn 'Hawkish'?
3. **The 'Real' Ask:** Is the Dollar strong because people *want* it, or because they *need* it to cover losses elsewhere (Check VIX)?
""")
