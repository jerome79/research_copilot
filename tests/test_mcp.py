# test_mcp_client.py
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mcp_client import MCPClient


def test_sentiment_panel_stats() -> None:
    """
    Test that MCPClient.sentiment_panel_stats handles the response correctly.
    Mocks the requests.post method to return a predefined JSON response.
    :return:
    """
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"stats": 1}
        mock_post.return_value.raise_for_status = lambda: None
        client = MCPClient()
        result = client.sentiment_panel_stats(["AAPL", "MSFT"], "2023-01-01", "2023-12-31")
        assert "stats" in result


def test_risk_summarize() -> None:
    """
    Test that MCPClient.risk_summarize handles the response correctly.
    Mocks the requests.post method to return a predefined JSON response.
    :return:
    """
    client = MCPClient()
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"risk": "ok"}
        mock_post.return_value.raise_for_status = lambda: None
        result = client.risk_summarize("AAPL", 2023)
        assert "risk" in result


def test_strategy_last_metrics() -> None:
    """
    Test that MCPClient.strategy_last_metrics handles the response correctly.
    Mocks the requests.get method to return a predefined JSON response.
    :return:
    """
    client = MCPClient()
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"metrics": "ok"}
        mock_get.return_value.raise_for_status = lambda: None
        result = client.strategy_last_metrics()
        assert "metrics" in result


def test_strategy_run_backtest() -> None:
    """
    Test that MCPClient.strategy_run_backtest handles the response correctly.
    Mocks the requests.post method to return a predefined JSON response.
    :return:
    """
    client = MCPClient()
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"backtest": "ok"}
        mock_post.return_value.raise_for_status = lambda: None
        result = client.strategy_run_backtest()
        assert "backtest" in result
