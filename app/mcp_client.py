import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

SENT_URL = os.getenv("SENTIMENT_BASE_URL", "http://localhost:8601")
RISK_URL = os.getenv("RISK_BASE_URL", "http://localhost:8602")
STRAT_URL = os.getenv("STRATEGY_BASE_URL", "http://localhost:8603")


class MCPClient:
    def sentiment_panel_stats(self, tickers: list, date_from: str, date_to: str) -> Any:
        """
        Fetches sentiment panel statistics for the given tickers and date range.

        Args:
            tickers (list): List of ticker symbols.
            date_from (str): Start date in YYYY-MM-DD format.
            date_to (str): End date in YYYY-MM-DD format.

        Returns:
            dict: JSON response containing panel statistics.
        """
        r = requests.post(f"{SENT_URL}/panel_stats", json={"tickers": tickers, "date_from": date_from, "date_to": date_to}, timeout=60)
        r.raise_for_status()
        return r.json()

    def risk_summarize(self, issuer: str, year: int, query: str = "top risks") -> Any:
        """
        Summarizes risk information for a given issuer and year.

        Args:
            issuer (str): The issuer's name or identifier.
            year (int): The year for risk summarization.
            query (str, optional): The risk query to execute. Defaults to "top risks".

        Returns:
            dict: JSON response containing summarized risk data.
        """
        r = requests.post(f"{RISK_URL}/summarize_risk", json={"issuer": issuer, "year": year, "query": query}, timeout=120)
        r.raise_for_status()
        return r.json()

    def strategy_last_metrics(self) -> Any:
        """
        Fetches the latest strategy metrics.

        Returns:
            dict: JSON response containing the latest strategy metrics.
        """
        r = requests.get(f"{STRAT_URL}/last_metrics", timeout=30)
        r.raise_for_status()
        return r.json()

    def strategy_run_backtest(self, factor: str = "SENT_L1", horizon: int = 1, universe: str = "SP500", costs_bps: int = 10) -> Any:
        """
        Runs a backtest for a given strategy factor and parameters.

        Args:
            factor (str): The strategy factor to backtest. Defaults to "SENT_L1".
            horizon (int): The investment horizon in days. Defaults to 1.
            universe (str): The universe of securities. Defaults to "SP500".
            costs_bps (int): Transaction costs in basis points. Defaults to 10.

        Returns:
            dict: JSON response containing backtest results.
        """
        r = requests.post(f"{STRAT_URL}/run_backtest", json={"factor": factor, "horizon": horizon, "universe": universe, "costs_bps": costs_bps}, timeout=180)
        r.raise_for_status()
        return r.json()
