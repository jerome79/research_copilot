import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.router import route_query


def test_sentiment_keywords() -> None:
    """
    Test that 'route_query' returns 'sentiment' for sentiment-related queries.
    """
    t, _, _ = route_query("show news sentiment for nvda")
    assert t == "sentiment"


def test_risk_keywords() -> None:
    """
    Test that 'route_query' returns 'risk' for risk-related queries.
    """
    t, _, _ = route_query("summarize 10-k item 1a risks")
    assert t == "risk"


def test_strategy_keywords() -> None:
    """
    Test that 'route_query' returns 'strategy' for strategy-related queries.
    """
    t, _, _ = route_query("what is the sharpe of the backtest")
    assert t == "strategy"


def test_route_query_sentiment():
    tool, conf, reason = route_query("positive news")
    assert tool == "sentiment"
    assert conf > 0
    assert "Matched" in reason


def test_route_query_override():
    tool, conf, reason = route_query("anything", override="risk")
    assert tool == "risk"
    assert conf == 1.0
    assert "Forced" in reason
