
A discretionary-PM style market monitoring dashboard built with Python + Streamlit.

This project focuses on market structure and positioning.

It transforms price and volume data into interpretable flow signals to help evaluate whether a move is early accumulation, systematic trend, or late crowded momentum.

 *Objective*

  Provide a daily framework to assess:
  
  Capital flow and participation
  
  Volatility regime shifts
  
  Crowding and fragility risk
  
  Trend maturity


 *Flow Framework*

Signals are derived from normalized market proxies:

Volume Z-Score (vol_z) → participation / crowding

ATR Z-Score (atr_z) → volatility expansion

Rolling Sharpe → trend persistence

Acceleration (accel_z) → parabolic behavior

RSI → momentum overheating


📊 Phase Classification

Quiet Accumulation
Low volume + contained volatility + clean trend.
Proxy for early institutional positioning.

Systematic Trend
Strong trend with moderate flow expansion.
Often reinforced by systematic strategies.

Late Crowded
High volume + volatility expansion + overheat signals.
Higher fragility and reversal risk.


🚫 Disclaimer

This tool is for market observation and research purposes only.
It does not provide trading signals or financial advice.
