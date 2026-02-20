import numpy as np
import pandas as pd
import yfinance as yf

R2_CONST = 0.25

def _load(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False).droplevel(['Ticker'],axis=1).dropna()
    return df

def _ret(df):
    return df["Close"].pct_change()

def _ols_beta_r2(y, x):
    """simple OLS with intercept; returns beta, r2"""
    d = pd.concat([y, x], axis=1).dropna()
    if len(d) < 60:
        return np.nan, np.nan
    yv = d.iloc[:,0].values
    xv = d.iloc[:,1].values
    X = np.column_stack([np.ones(len(xv)), xv])
    # OLS
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    yhat = X @ b
    ss_res = ((yv - yhat)**2).sum()
    ss_tot = ((yv - yv.mean())**2).sum()
    r2 = 1 - ss_res/ss_tot if ss_tot != 0 else np.nan
    beta = b[1]
    return float(beta), float(r2)

def _z(s, w=60):
    return (s - s.rolling(w).mean()) / s.rolling(w).std(ddof=0)

def _atr_pct(df, period=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    prev = close.shift(1)
    tr = pd.concat([(high-low).abs(), (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    return atr / close

def _rsi(close, period=14):
    d = close.diff()
    g = d.clip(lower=0.0)
    l = (-d).clip(lower=0.0)
    ag = g.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    al = l.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = ag / al.replace(0, np.nan)
    return 100 - 100/(1+rs)

def explain_stock(ticker: str, sector_etf: str = None, start='2022-01-01', end='2026-01-01'):
    """
    Returns:
      - metrics: dict
      - narrative: str (PM-style explanation)
      - table: pd.DataFrame (key recent indicators)
    """
    px = _load(ticker, start=start, end=end)
    spy = _load("SPY", start=start, end=end)

    y = _ret(px)
    x_mkt = _ret(spy)

    beta_mkt, r2_mkt = _ols_beta_r2(y, x_mkt)

    beta_sec, r2_sec = (np.nan, np.nan)
    if sector_etf:
        sec = _load(sector_etf, start=start, end=end)
        x_sec = _ret(sec)
        beta_sec, r2_sec = _ols_beta_r2(y, x_sec)

    # shape / crowding proxies
    ret = y
    vol_z = _z(np.log1p(px["Volume"]), 60)
    atrp = _atr_pct(px)
    atr_z = _z(atrp, 60)

    accel = px["Close"].pct_change().diff().rolling(10).mean()
    accel_z = _z(accel, 60)

    rsi = _rsi(px["Close"], 14)

    # jumpiness / gapiness
    gap = (px["Open"] / px["Close"].shift(1) - 1).abs()
    gap_rate = float((gap > gap.rolling(60).std(ddof=0)*2).rolling(60).mean().iloc[-1])

    big_move = (ret.abs() > ret.rolling(60).std(ddof=0)*2)
    big_move_rate = float(big_move.rolling(60).mean().iloc[-1])

    # latest
    last = px.index[-1]
    m = {
        "date": str(last.date()),
        "beta_vs_spy": beta_mkt,
        "r2_vs_spy": r2_mkt,
        "beta_vs_sector": beta_sec,
        "r2_vs_sector": r2_sec,
        "vol_z": float(vol_z.iloc[-1]),
        "atr_z": float(atr_z.iloc[-1]),
        "accel_z": float(accel_z.iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
        "gap_jump_rate_60d": gap_rate,
        "big_move_rate_60d": big_move_rate,
    }

    # PM-style narrative rules (simple but effective)
    parts = []

    # Driver
    if np.isfinite(r2_mkt) and r2_mkt < R2_CONST:
        parts.append(
            "Recently the stock appears more **idiosyncratic**, with low explanatory power from the broad market. "
            "The move is likely driven by company-specific, event-driven, or thematic factors."
        )
    elif np.isfinite(beta_mkt) and beta_mkt > 1.2:
        parts.append(
            "The stock shows **high beta** to the broad market and behaves more like a risk-on / risk-off amplifier."
        )
    else:
        parts.append(
            "The stock has moderate correlation with the market, suggesting a mix of beta exposure and idiosyncratic drivers."
        )

    if sector_etf and np.isfinite(r2_sec):
        if r2_sec > r2_mkt + 0.15:
            parts.append(
                f"The move appears more aligned with **sector beta**, with stronger explanatory power from {sector_etf} than SPY."
            )
        elif r2_sec < R2_CONST:
            parts.append(
                "Low explanatory power from the sector further supports a **single-stock narrative or event-driven** dynamic."
            )

    # Crowding / fragility
    crowded_flags = []
    if m["vol_z"] > 1.0: crowded_flags.append("elevated trading volume")
    if m["atr_z"] > 1.0: crowded_flags.append("volatility expansion")
    if m["accel_z"] > 1.0: crowded_flags.append("price acceleration (parabolic risk)")
    if m["rsi"] > 70: crowded_flags.append("overbought RSI conditions")

    if len(crowded_flags) >= 2:
        parts.append(
            "Current signals suggest **crowding / fragility**, including: "
            + ", ".join(crowded_flags) + "."
        )
        parts.append(
            "From a PM perspective, it may be preferable to wait for pullbacks or volume compression before adding risk, "
            "or to trail stops higher rather than chasing strength."
        )
    else:
        parts.append(
            "No clear signs of late-stage crowding at the moment (volume and volatility are not jointly elevated, "
            "and acceleration remains contained)."
        )

    # Shape
    if m["gap_jump_rate_60d"] > 0.12 or m["big_move_rate_60d"] > 0.12:
        parts.append(
            "Price action appears more **jump-driven**, with a higher frequency of gaps or large moves, "
            "often associated with news flow or positioning shifts."
        )
    else:
        parts.append(
            "Price action appears more **grind-up / trend-like**, consistent with gradual re-rating or quiet accumulation."
        )

    narrative = " ".join(parts)


    table = pd.DataFrame({
        "Close": px["Close"],
        "vol_z": vol_z,
        "atr_z": atr_z,
        "accel_z": accel_z,
        "rsi": rsi
    }).tail(60)

    return m, narrative, table
