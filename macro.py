import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Macro Quant Terminal V2")

# --- 1. DATA ENGINE ---
@st.cache_data(ttl=3600)
def get_macro_data():
    tickers = {
        "DXY": "DX-Y.NYB",
        "US_10Y": "^TNX",
        "Copper": "HG=F",
        "Gold": "GC=F",
        "VIX": "^VIX",
        "SPY": "SPY"
    }
    data = yf.download(list(tickers.values()), period="1y", interval="1d")['Close']
    inv_tickers = {v: k for k, v in tickers.items()}
    return data.rename(columns=inv_tickers)

df = get_macro_data()

# --- 2. Z-SCORE CALCULATIONS ---
def calculate_zscore(series, window=20):
    # Standard Z-Score formula: (Price - Mean) / Standard Deviation
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    return (series - rolling_mean) / rolling_std

# Apply Z-Score to all major columns
z_cols = ['DXY', 'US_10Y', 'VIX', 'SPY']
for col in z_cols:
    df[f'{col}_Z'] = calculate_zscore(df[col])

# --- 3. DASHBOARD UI ---
st.title("🏛️ Institutional Macro Terminal")
st.markdown("### Statistical Edge: Z-Score Analysis")

# Metric Row
c1, c2, c3, c4 = st.columns(4)
metrics = [("DXY", "DXY_Z"), ("10Y Yield", "US_10Y_Z"), ("VIX", "VIX_Z"), ("S&P 500", "SPY_Z")]

for i, (name, col_z) in enumerate(metrics):
    current_z = df[col_z].iloc[-1]
    with [c1, c2, c3, c4][i]:
        # Color coding the Z-score for quick reading
        color = "inverse" if abs(current_z) > 2 else "normal"
        st.metric(f"{name} Z-Score", f"{current_z:.2f}σ", delta_color=color)

st.divider()

# --- 4. THE BIAS ENGINE (Z-SCORE LOGIC) ---
st.subheader("📊 Mathematical Bias Engine")
col_left, col_right = st.columns([2, 1])

with col_left:
    # Charting the Z-score of the Dollar
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index[-60:], y=df['DXY_Z'].tail(60), name="DXY Z-Score", line=dict(color='cyan')))
    # Add Extreme Threshold Lines
    fig.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="Overbought (+2σ)")
    fig.add_hline(y=-2.0, line_dash="dash", line_color="green", annotation_text="Oversold (-2σ)")
    fig.update_layout(title="US Dollar Index (DXY) Statistical Stretch", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.write("**Current Market Condition:**")
    dxy_z = df['DXY_Z'].iloc[-1]
    
    if dxy_z > 2.0:
        st.error("🚨 DXY is EXTREMELY OVERBOUGHT. Statistically, the USD should cool off here. High probability for a 'Sell the Rip' week.")
    elif dxy_z < -2.0:
        st.success("✅ DXY is EXTREMELY OVERSOLD. Look for a 'Mean Reversion' bounce. Bearish for stocks, Bullish for USD.")
    else:
        st.info("⚖️ DXY is in a Normal Range. Direction will be driven by news flow (NFP, CPI) rather than math.")

st.divider()
st.subheader("🧭 How to Trade This:")
st.write("""
1.  **Mean Reversion:** When an asset hits **±2.0σ**, it is like a rubber band pulled to its limit. It wants to snap back to 0. 
2.  **Confluence:** If **DXY Z-Score is +2.0** AND **VIX Z-Score is -2.0**, you have a perfect setup to Short USD and Buy Stocks, because fear is too low and the dollar is too high.
""")
