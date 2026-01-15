import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Macro Quant Terminal")

# --- DATA ENGINE ---
@st.cache_data(ttl=3600)
def fetch_macro_data():
    # Adding 2-Year Yields for US, Germany (Eurozone), and Japan
    tickers = {
        "DXY": "DX-Y.NYB",
        "US_2Y": "ZT=F",    # US 2Y Treasury Note Futures
        "GER_2Y": "FGBS.EX", # Euro Schatz (German 2Y)
        "JPY_2Y": "2YY=F",   # Japan 2Y Yield
        "Copper": "HG=F",
        "Gold": "GC=F",
        "VIX": "^VIX"
    }
    # Fetching 1-year of daily data
    data = yf.download(list(tickers.values()), period="1y", interval="1d")['Close']
    inv_tickers = {v: k for k, v in tickers.items()}
    return data.rename(columns=inv_tickers)

df = fetch_macro_data()

# --- CALCULATIONS ---
# 1. Spread US vs Germany (EUR/USD Driver)
df['US_GER_Spread'] = df['US_2Y'] - df['GER_2Y']

# 2. Spread US vs Japan (USD/JPY Driver)
df['US_JPY_Spread'] = df['US_2Y'] - df['JPY_2Y']

# --- HEADER ---
st.title("🏛️ Professional Macro Terminal (Institutional View)")

# --- SECTION 1: CENTRAL BANK POLICY RATES (Static Data for 2026) ---
st.subheader("🌍 Central Bank Policy Rates (Jan 2026)")
rate_data = {
    "Country": ["USA (Fed)", "Eurozone (ECB)", "UK (BoE)", "Japan (BoJ)", "Australia (RBA)"],
    "Current Rate": ["3.75%", "2.15%", "3.75%", "0.75%", "3.60%"],
    "Last Move": ["-25bps Cut", "Hold", "-25bps Cut", "+25bps Hike", "Hold"],
    "Sentiment": ["Dovish", "Neutral", "Dovish", "Hawkish", "Hawkish"]
}
st.table(pd.DataFrame(rate_data))

# --- SECTION 2: THE FX DRIVERS (YIELD SPREADS) ---
st.divider()
st.subheader("📈 Yield Differentials (The Real FX Drivers)")
col1, col2 = st.columns(2)

with col1:
    st.write("**US vs Germany 2Y Spread** (Leads EURUSD)")
    # If the spread goes UP, EURUSD usually goes DOWN
    fig1 = go.Figure(go.Scatter(x=df.index[-60:], y=df['US_GER_Spread'].tail(60), line=dict(color='cyan')))
    fig1.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.write("**US vs Japan 2Y Spread** (Leads USDJPY)")
    # If the spread goes DOWN, USDJPY usually goes DOWN (Yen Strength)
    fig2 = go.Figure(go.Scatter(x=df.index[-60:], y=df['US_JPY_Spread'].tail(60), line=dict(color='yellow')))
    fig2.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig2, use_container_width=True)

# --- SECTION 3: THE "CARRY TRADE" DASHBOARD ---
st.divider()
st.subheader("💰 Carry Trade Viability")
st.write("Professional traders borrow low-interest currencies (Yen) to buy high-interest ones (USD).")

# Simple Carry Score: Spread / VIX
# High Spread + Low VIX = Good for Carry. High VIX = Carry Unwind (Market Crash).
current_vix = df['VIX'].iloc[-1]
carry_score = (df['US_JPY_Spread'].iloc[-1] / current_vix) * 10

st.info(f"**Current Carry Score:** {carry_score:.2f} | **VIX Check:** {current_vix:.2f}")
if current_vix > 20:
    st.error("🚨 WARNING: High Volatility. Carry trades are likely UNWINDING. Safe Haven flows into Yen/Dollar.")
else:
    st.success("✅ Calm Markets. High-yield currencies should remain supported.")
