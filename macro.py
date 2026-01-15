import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Global Macro Terminal")

# --- DATA ENGINE (NO API KEY REQUIRED) ---
@st.cache_data(ttl=3600)
def fetch_terminal_data():
    # Tickers: 13-week Treasury (^IRX), 10Y Yield (^TNX), DXY (DX-Y.NYB)
    # Bunds (DE10Y.B), Gilts (GBP10Y-GB), Copper (HG=F), Gold (GC=F)
    tickers = {
        "DXY": "DX-Y.NYB",
        "EURUSD": "EURUSD=X",
        "USDJPY": "JPY=X",
        "US_10Y": "^TNX",
        "US_2Y": "^ZTN=F", # 2Y Note Futures as proxy
        "Copper": "HG=F",
        "Gold": "GC=F",
        "VIX": "^VIX"
    }
    
    data = yf.download(list(tickers.values()), period="1y", interval="1d")['Close']
    # Rename columns back to readable names
    inv_tickers = {v: k for k, v in tickers.items()}
    data = data.rename(columns=inv_tickers)
    return data

df = fetch_terminal_data()

# --- CALCULATIONS ---
# Copper/Gold Ratio (Risk Barometer)
df['Cu_Au_Ratio'] = df['Copper'] / df['Gold']

# Weekly Change % for Dashboard
weekly_change = ((df.iloc[-1] - df.iloc[-5]) / df.iloc[-5] * 100)

# --- HEADER SECTION ---
st.title("🏛️ Professional Macro Terminal (Weekly Outlook)")
st.markdown(f"**Last Update:** {df.index[-1].strftime('%Y-%m-%d')} | **Market Regime:** {'Risk-Off (USD Strong)' if df['VIX'].iloc[-1] > 20 else 'Risk-On (USD Weak)'}")

# --- ROW 1: THE BIG THREE (BIAS INDICATORS) ---
col1, col2, col3 = st.columns(3)

with col1:
    val = df['DXY'].iloc[-1]
    change = weekly_change['DXY']
    st.metric("Dollar Index (DXY)", f"{val:.2f}", f"{change:.2f}% (Weekly)")
    fig = go.Figure(go.Scatter(x=df.index[-30:], y=df['DXY'].iloc[-30:], line=dict(color='#00ffcc')))
    fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    val = df['US_10Y'].iloc[-1]
    change = weekly_change['US_10Y']
    st.metric("US 10Y Yield (%)", f"{val:.2f}%", f"{change:.2f}% (Weekly)")
    fig = go.Figure(go.Scatter(x=df.index[-30:], y=df['US_10Y'].iloc[-30:], line=dict(color='#ffaa00')))
    fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    val = df['Cu_Au_Ratio'].iloc[-1]
    change = weekly_change['Cu_Au_Ratio']
    st.metric("Copper/Gold Ratio", f"{val:.4f}", f"{change:.2f}% (Weekly)")
    fig = go.Figure(go.Scatter(x=df.index[-30:], y=df['Cu_Au_Ratio'].iloc[-30:], line=dict(color='#ff00ff')))
    fig.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- ROW 2: WEEKLY CONVICTION TABLE ---
st.divider()
st.subheader("📊 Weekly Macro Conviction Matrix")

# Logic for Bias
def determine_bias(row):
    if row['Indicator'] == 'DXY' and row['Wk_Change'] > 0: return "Bullish / Short-Squeeze"
    if row['Indicator'] == 'Cu_Au_Ratio' and row['Wk_Change'] < 0: return "Risk-Off (Buy USD)"
    if row['Indicator'] == 'US_10Y' and row['Wk_Change'] < 0: return "Dovish (Short USD)"
    return "Neutral / Rangebound"

matrix_df = pd.DataFrame({
    "Indicator": ["DXY", "US_10Y", "Cu_Au_Ratio", "VIX", "EURUSD"],
    "Current": [df['DXY'].iloc[-1], df['US_10Y'].iloc[-1], df['Cu_Au_Ratio'].iloc[-1], df['VIX'].iloc[-1], df['EURUSD'].iloc[-1]],
    "Wk_Change": [weekly_change['DXY'], weekly_change['US_10Y'], weekly_change['Cu_Au_Ratio'], weekly_change['VIX'], weekly_change['EURUSD']]
})
matrix_df['Actionable Bias'] = matrix_df.apply(determine_bias, axis=1)

st.table(matrix_df.style.format({"Current": "{:.2f}", "Wk_Change": "{:.2f}%"}))

# --- ROW 3: GLOBAL BOND MAP (INTERN EXPLANATION) ---
st.divider()
st.subheader("🧭 Junior Intern Macro Map")
st.write("""
**How to use this for your Weekly Bias:**
1. **DXY vs 10Y Yield:** If the 10Y Yield is falling but DXY is rising, it's a **Fake Move**. The Dollar will likely crash later in the week.
2. **Copper/Gold Ratio:** If this ratio breaks its 1-month low, exit all your currency shorts. It means a recession scare is starting.
3. **VIX Check:** If VIX is moving from 12 toward 18, stop shorting the Dollar. Capital is running for cover.
""")