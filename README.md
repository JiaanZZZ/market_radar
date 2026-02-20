
A discretionary-PM style market monitoring dashboard built with Python + Streamlit. This project focuses on market structure and positioning. It transforms price and volume data into interpretable flow signals to help evaluate whether a move is early accumulation, systematic trend, or late crowded momentum.

 **Objective**

  Provide a daily framework to assess:
  
  1. Capital flow and participation
  
  2. Volatility regime shifts
  
  3. Crowding and fragility risk
  
  4. Trend maturity


 **Flow Framework**

Signals are derived from normalized market proxies:

  1. Volume Z-Score (vol_z) → participation / crowding

  2. ATR Z-Score (atr_z) → volatility expansion
  
  3. Rolling Sharpe → trend persistence
  
  4. Acceleration (accel_z) → parabolic behavior
  
  5. RSI → momentum overheating


**Phase Classification**

*Quiet Accumulation*
Low volume + contained volatility + clean trend.
Proxy for early institutional positioning.

*Systematic Trend*
Strong trend with moderate flow expansion.
Often reinforced by systematic strategies.

*Late Crowded*
High volume + volatility expansion + overheat signals.
Higher fragility and reversal risk.


<img width="1707" height="884" alt="Screenshot 2026-02-20 at 19 19 48" src="https://github.com/user-attachments/assets/41fe6dce-0d50-49a1-b097-544ae37caa4c" />





