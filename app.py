import streamlit as st
from universe import WATCHLIST
from radar_engine import scan_universe, load_price, SHARPE_CONST, VOL_CONST, ACC_CONST,ATZ_CONST,RSI_CONST
# app.py 里（你已有的基础上加）
import streamlit as st
from pm_explainer import explain_stock
import altair as alt

SECTOR_ETF_BY_SECTOR = {
    "Technology": "XLK",
    "Financial Services": "XLF",   # yfinance sometimes calls it this
    "Financial": "XLF",
    "Healthcare": "XLV",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Basic Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
}

INDUSTRY_HINTS = {
    # Semis
    "Semiconductors": "SOXX",        # or "SMH"
    "Semiconductor Equipment": "SOXX",
    "Semiconductor": "SOXX",

    # Banks
    "Banks": "KBE",                  # or "KRE" for regional banks
    "Regional Banks": "KRE",

    # Software
    "Software": "IGV",

    # Biotech
    "Biotechnology": "XBI",          # or "IBB"

    # Internet / Cloud-ish
    "Internet Content & Information": "FDN",
    "Internet Retail": "XLY",

    # Energy sub-themes
    "Oil & Gas E&P": "XOP",
    "Oil & Gas Equipment & Services": "OIH",

    # China / EM examples
    "China": "MCHI",
}

import yfinance as yf

def map_stock_to_etf(ticker: str) -> dict:
    """
    Returns a dict:
      {
        "sector": ...,
        "industry": ...,
        "sector_etf": ...,
        "industry_etf": ...
      }
    """
    info = yf.Ticker(ticker).info or {}
    sector = info.get("sector")
    industry = info.get("industry")

    sector_etf = SECTOR_ETF_BY_SECTOR.get(sector)
    industry_etf = None

    # try industry-based hints (substring match)
    if industry:
        for k, etf in INDUSTRY_HINTS.items():
            if k.lower() in industry.lower():
                industry_etf = etf
                break

    # choose best available
    chosen = industry_etf or sector_etf

    return {
        "ticker": ticker,
        "sector": sector,
        "industry": industry,
        "sector_etf": sector_etf,
        "industry_etf": industry_etf,
        "chosen_etf": chosen,
    }

    m = map_stock_to_etf("NVDA")
    print(m)
    # typically chosen_etf -> SOXX


SECTOR_MAP = {
    "NVDA": "SOXX",
    "AMD": "SOXX",
    "AVGO": "SOXX",
    "JPM": "XLF",
    "GS": "XLF",
    "XOM": "XLE",
    "LLY": "XLV",
    "LITE":"IYZ"
}

import datetime as dt

st.sidebar.header("Backtest Window")

start_date = st.sidebar.date_input(
    "Start Date",
    value=dt.date(2023,1,1)
)

end_date = st.sidebar.date_input(
    "End Date",
    value=dt.date.today()
)


ticker = st.sidebar.selectbox("Select Ticker", WATCHLIST,key=1)
refresh = st.sidebar.button("🔄 Refresh Radar")

sector_etf = map_stock_to_etf(ticker)['sector_etf']

st.set_page_config(layout="wide")
if refresh:


    metrics, narrative, table = explain_stock(ticker, sector_etf=sector_etf,start=str(start_date),end=str(end_date))



    st.subheader("🧠 PM Explanation")
    st.write(narrative)

    st.subheader("📌 Key Metrics")
    st.json(metrics)

    st.subheader("📊 Last 60 days indicators")
    st.dataframe(table)




    st.title("📡 Market Flow Radar")

    st.write("Quiet Accumulation = early smart money proxy")
    st.write("Late Crowded = flow exhaustion risk")

    st.write(f''' Benchmark Values: \n
                    Sharpe: {SHARPE_CONST} \n
                    Volume z-score: {VOL_CONST} \n
                    ATZ: {ATZ_CONST}\n
                    RSI: {RSI_CONST} \n
                    Acceleration: {ACC_CONST}
             ''')



    df = scan_universe(WATCHLIST,start_date, end_date)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 Quiet Accumulation")
        st.dataframe(df.sort_values("quiet_score",ascending=False))

    with col2:
        st.subheader("🔴 Late Crowded")
        st.dataframe(df.sort_values("crowded_score",ascending=False))

    st.subheader("🔎 Single Stock View")


    price = load_price(ticker,start=start_date,end=end_date)
    st.write('close')
    st.line_chart(table["Close"])

    st.write('volatility')
    st.line_chart(table["atr_z"],color='Orange')



else:
    st.write("Please choose your stock and dates")


