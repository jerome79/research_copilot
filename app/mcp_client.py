import os, requests
from dotenv import load_dotenv
load_dotenv()

SENT_URL = os.getenv("SENTIMENT_BASE_URL","http://localhost:8601")
RISK_URL = os.getenv("RISK_BASE_URL","http://localhost:8602")
STRAT_URL= os.getenv("STRATEGY_BASE_URL","http://localhost:8603")

class MCPClient:
    def sentiment_panel_stats(self, tickers, date_from, date_to):
        r = requests.post(f"{SENT_URL}/panel_stats",
                          json={"tickers": tickers, "date_from": date_from, "date_to": date_to}, timeout=60)
        r.raise_for_status()
        return r.json()

    def risk_summarize(self, issuer, year, query="top risks"):
        r = requests.post(f"{RISK_URL}/summarize_risk",
                          json={"issuer": issuer, "year": year, "query": query}, timeout=120)
        r.raise_for_status()
        return r.json()

    def strategy_last_metrics(self):
        r = requests.get(f"{STRAT_URL}/last_metrics", timeout=30)
        r.raise_for_status()
        return r.json()

    def strategy_run_backtest(self, factor="SENT_L1", horizon=1, universe="SP500", costs_bps=10):
        r = requests.post(f"{STRAT_URL}/run_backtest",
                          json={"factor": factor, "horizon": horizon, "universe": universe, "costs_bps": costs_bps}, timeout=180)
        r.raise_for_status()
        return r.json()
