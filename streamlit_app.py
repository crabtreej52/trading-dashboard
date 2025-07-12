import os
import pandas as pd
import yfinance as yf
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 minutes (600,000 ms)
st_autorefresh(interval=600000, key="auto_refresh")

# Load .env if running locally
load_dotenv()

st.set_page_config(page_title="📈 My Personal Trading Assistant")
st.title("📈 My Personal Trading Assistant")

symbols = ["EAT", "CART", "LLOY.L"]

for symbol in symbols:
    st.subheader(symbol)
    try:
        df = yf.download(symbol, period="3mo")
        if df.empty:
            raise Exception("No data returned")

        df['Change'] = df['Close'].diff()
        df['Gain'] = df['Change'].apply(lambda x: x if x > 0 else 0)
        df['Loss'] = df['Change'].apply(lambda x: -x if x < 0 else 0)
        avg_gain = df['Gain'].rolling(window=14).mean()
        avg_loss = df['Loss'].rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        latest = df.dropna().iloc[-1]  # ensure we don't pick up NaNs

        close = float(latest['Close'])
        rsi = float(latest['RSI'])
        macd = float(latest['MACD'])
        signal = float(latest['Signal'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Close Price", f"{close:.2f}")
        col2.metric("RSI", f"{rsi:.2f}")
        col3.metric("MACD", f"{macd:.2f}")
        col4.metric("MACD Signal", f"{signal:.2f}")

        # Suggest action
        if rsi < 40:
            suggestion = "✅ Buy"
            explanation = "RSI is low – may be oversold."
        elif macd > signal:
            suggestion = "✅ Buy"
            explanation = "MACD crossed above signal."
        else:
            suggestion = "📦 Hold"
            explanation = "No clear signal."

        st.markdown(f"**Your action for {symbol}:**")
        st.radio(
    "",
    ["None", "✅ Buy", "📦 Hold", "❌ Skip"],
    index=["✅ Buy", "📦 Hold", "❌ Skip"].index(suggestion),
    key=f"action_{symbol}"
)

        st.caption(explanation)

    except Exception as e:
        st.error(f"Error loading data for {symbol}: {e}")

    st.markdown("---")
