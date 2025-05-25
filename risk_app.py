import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Investment Risk Analyzer", layout="centered")
st.title("Investment Risk Analyzer")

st.markdown("---")
st.markdown("### Stock Input")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Stock Ticker (e.g., AAPL, MSFT, TSLA)", value="AAPL")
with col2:
    investment = st.number_input("Investment Amount (USD)", min_value=100.0, step=100.0)

st.markdown("---")

weights = {
    "volatility": 0.25,
    "max_drawdown": 0.10,
    "beta": 0.05,
    "sector": 0.05,
    "concentration": 0.05,
    "debt_to_equity": 0.20,
    "operating_margin": 0.10,
    "dividend_yield": 0.03,
    "ps_ratio": 0.10,
    "forward_pe": 0.07
}

sector_risk_map = {
    "Technology": 60,
    "Energy": 80,
    "Healthcare": 40,
    "Financial Services": 55,
    "Industrials": 65,
    "Consumer Defensive": 35,
    "Utilities": 30,
    "Communication Services": 50,
    "Consumer Cyclical": 70,
    "Basic Materials": 60,
    "Real Estate": 70,
    "Unknown": 50
}

if st.button("Analyze Risk") and ticker:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty:
            st.error("Failed to load historical price data.")
        else:
            info = stock.info
            close = hist["Close"]
            returns = close.pct_change().dropna()

            # Indicator calculations
            volatility = np.std(returns)
            volatility_score = min(volatility * 1000, 100)

            running_max = close.cummax()
            drawdown = (close - running_max) / running_max
            max_dd = drawdown.min()
            drawdown_score = min(abs(max_dd) * 100, 100)

            beta = info.get("beta", None)
            beta_score = min(abs(beta) * 50, 100) if beta is not None else 70

            sector = info.get("sector", "Unknown")
            sector_score = sector_risk_map.get(sector, 50)

            concentration_score = 80  # Fixed

            dte = info.get("debtToEquity", None)
            debt_score = min(float(dte) * 0.2, 100) if dte is not None and dte >= 0 else 70

            margin = info.get("operatingMargins", None)
            margin_score = 100 - (margin * 200) if margin is not None else 70
            margin_score = max(min(margin_score, 100), 0)

            div_yield = info.get("dividendYield", None)
            div_score = 70 - (div_yield * 1000) if div_yield is not None else 70
            div_score = max(min(div_score, 100), 0)

            ps = info.get("priceToSalesTrailing12Months", None)
            ps_score = min(ps * 10, 100) if ps is not None else 70

            pe = info.get("forwardPE", None)
            pe_score = min(pe * 3, 100) if pe is not None and pe > 0 else 90

            risk_percent = (
                weights["volatility"] * volatility_score +
                weights["max_drawdown"] * drawdown_score +
                weights["beta"] * beta_score +
                weights["sector"] * sector_score +
                weights["concentration"] * concentration_score +
                weights["debt_to_equity"] * debt_score +
                weights["operating_margin"] * margin_score +
                weights["dividend_yield"] * div_score +
                weights["ps_ratio"] * ps_score +
                weights["forward_pe"] * pe_score
            )

            st.markdown("---")
            st.markdown("### Overall Risk")
            risk_level = "Very Low" if risk_percent <= 20 else \
                         "Low" if risk_percent <= 40 else \
                         "Moderate" if risk_percent <= 60 else \
                         "High" if risk_percent <= 80 else "Very High"

            risk_color = "#d4edda" if risk_percent <= 40 else ("#fff3cd" if risk_percent <= 80 else "#f8d7da")

            st.markdown(f"""
                <div style='background-color:{risk_color};padding:15px;border-radius:10px;border:1px solid #ccc;'>
                    <h3>Overall Risk: {round(risk_percent, 1)}%</h3>
                    <p style='font-size:16px;'>Risk Level: <strong>{risk_level}</strong></p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Breakdown by Indicator")
            df = pd.DataFrame({
                "Indicator": [
                    "Volatility", "Max Drawdown", "Beta", "Sector Risk", "Concentration",
                    "Debt to Equity", "Operating Margin", "Dividend Yield", "P/S Ratio", "Forward P/E"
                ],
                "Score": [
                    round(volatility_score), round(drawdown_score), round(beta_score),
                    round(sector_score), round(concentration_score), round(debt_score),
                    round(margin_score), round(div_score), round(ps_score), round(pe_score)
                ]
            })
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
