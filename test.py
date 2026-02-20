from pm_explainer import _load, explain_stock
from radar_engine import score_stock

df = _load('NVDA')
score_stock(df)
# explain_stock('NVDA', 'SOXX', start="2022-01-01")