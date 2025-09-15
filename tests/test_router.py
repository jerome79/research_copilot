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
