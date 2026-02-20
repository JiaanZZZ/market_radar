import numpy as np
import pandas as pd
import yfinance as yf

SHARPE_CONST = 0.5
VOL_CONST = 0.8
ATZ_CONST = 0.8
RSI_CONST = 72
ACC_CONST = 0.6


def zscore(s, w=60):
    return (s - s.rolling(w).mean()) / s.rolling(w).std()

def rsi(close, period=14):
    d = close.diff()
    g = d.clip(lower=0).rolling(period).mean()
    l = (-d.clip(upper=0)).rolling(period).mean()
    rs = g/l
    return 100 - 100/(1+rs)

def atr_pct(df):
    high, low, close = df["High"], df["Low"], df["Close"]
    prev = close.shift()
    tr = pd.concat([(high-low),(high-prev).abs(),(low-prev).abs()],axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    return atr/close

def load_price(ticker,start,end):
    df = yf.download(ticker, start=start, end=end,auto_adjust=True, progress=False)
    return df.droplevel(['Ticker'],axis=1).dropna()

def score_stock(df):

    close = df["Close"]
    ret = close.pct_change()

    vol_z = zscore(np.log1p(df["Volume"])).iloc[-1]
    atr_z = zscore(atr_pct(df)).iloc[-1]
    r = rsi(close).iloc[-1]

    mu = ret.rolling(20).mean().iloc[-1]
    sd = ret.rolling(20).std().iloc[-1]
    sharpe = (mu/sd)*np.sqrt(252) if sd!=0 else 0

    accel = close.pct_change().diff().rolling(10).mean()
    accel_z = zscore(accel).iloc[-1]



    # quiet accumulation
    quiet = np.nanmean([
        np.clip((sharpe-SHARPE_CONST)/2,0,1),
        np.clip((VOL_CONST-vol_z)/2,0,1),
        np.clip((ATZ_CONST-atr_z)/2,0,1),
        np.clip((RSI_CONST-r)/20,0,1),
        np.clip((ACC_CONST-accel_z)/2,0,1),
    ])

    # crowded
    crowded = np.nanmean([
        np.clip((vol_z-VOL_CONST)/1.5,0,1),
        np.clip((atr_z-ATZ_CONST)/1.5,0,1),
        np.clip((r-RSI_CONST)/20,0,1),
        np.clip((accel_z-ACC_CONST)/1.5,0,1),
    ])

    if crowded>0.7:
        label="Late Crowded"
    elif quiet>0.65:
        label="Quiet Accumulation"
    else:
        label="Neutral"

    return {
        "quiet_score":quiet,
        "crowded_score":crowded,
        "label":label,
        "rsi":r,
        "vol_z":vol_z,
        "atr_z":atr_z,
        "sharpe":sharpe,
        "accel_z":accel_z
    }

def scan_universe(tickers, start_date, end_date):

    rows=[]

    for t in tickers:
        try:
            df=load_price(t,start_date,end_date)
            if len(df)<100:
                continue
            s=score_stock(df)
            s["ticker"]=t
            rows.append(s)
        except:
            continue

    return pd.DataFrame(rows).set_index("ticker")
