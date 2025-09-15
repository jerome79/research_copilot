# tests/test_ui_streamlit.py
from app.ui_streamlit import _plot_sentiment


def test_plot_sentiment_returns_image():
    # Provide sample sentiment data
    data = [
        {"ticker": "AAPL", "date": "2024-01-01", "avg_sentiment": 0.5},
        {"ticker": "AAPL", "date": "2024-01-02", "avg_sentiment": 0.6},
        {"ticker": "MSFT", "date": "2024-01-01", "avg_sentiment": 0.4},
    ]
    img = _plot_sentiment(data)
    assert img is not None
    assert hasattr(img, "read")


def test_plot_sentiment_empty():
    # Should return None for empty data
    assert _plot_sentiment([]) is None


def test_route_query_sentiment(monkeypatch):
    def mock_panel_stats(symbols, dfrom, dto, panel_path=None):
        return {
            "stats": {"count": 2},
            "series": [
                {"ticker": "AAPL", "date": "2024-01-01", "avg_sentiment": 0.5},
                {"ticker": "MSFT", "date": "2024-01-01", "avg_sentiment": 0.4},
            ],
        }

    from app.ui_streamlit import run_sentiment

    stats, img, df = run_sentiment(mock_panel_stats, "AAPL,MSFT", "2024-01-01", "2024-01-02", "dummy_path")
    assert stats["count"] == 2
    assert img is not None
    assert not df.empty


def test_run_risk(monkeypatch):
    def mock_risk_summarize(issuer, year, question):
        return {"summary": "Risk summary text", "categories": [{"cat": "Liquidity"}], "sources": ["source1", "source2"]}

    from app.ui_streamlit import run_risk

    summary, categories, sources = run_risk(mock_risk_summarize, "AAPL", 2023, "top risks", None)
    assert "Risk summary" in summary
    assert not categories.empty
    assert sources == ["source1", "source2"]


def test_run_strategy(monkeypatch):
    def mock_last_metrics():
        return {"metrics": {"IC": None}, "equity_curve_path": None}

    def mock_run_bt_from_panel(panel_path=None, factor=None, horizon=None):
        return {"metrics": {"IC": 0.5}, "equity_curve_path": "curve.png"}

    from app.ui_streamlit import run_strategy

    metrics, curve_path = run_strategy(mock_last_metrics, mock_run_bt_from_panel, "SENT_L1", 1, "dummy_path")
    assert metrics["IC"] == 0.5
    assert curve_path == "curve.png"


def test_run_sentiment_panel_path(monkeypatch):
    # Test run_sentiment with panel_path argument
    def mock_panel_stats(symbols, dfrom, dto, panel_path=None):
        assert panel_path == "dummy_path"
        return {"stats": {"count": 1}, "series": [{"ticker": "AAPL", "date": "2024-01-01", "avg_sentiment": 0.5}]}

    from app.ui_streamlit import run_sentiment

    stats, img, df = run_sentiment(mock_panel_stats, "AAPL", "2024-01-01", "2024-01-02", "dummy_path")
    assert stats["count"] == 1
    assert img is not None
    assert not df.empty


def test_run_risk_with_data_dir(monkeypatch):
    # Test run_risk with risk_data_dir argument
    def mock_risk_summarize(issuer, year, question):
        return {"summary": "Risk summary with dir", "categories": [{"cat": "Market"}], "sources": ["sourceA"]}

    import os

    from app.ui_streamlit import run_risk

    summary, categories, sources = run_risk(mock_risk_summarize, "AAPL", 2023, "top risks", "test_dir")
    assert "dir" in summary
    assert not categories.empty
    assert sources == ["sourceA"]
    assert os.environ["RISK_DATA_DIR"] == "test_dir"


def test_run_strategy_no_ic(monkeypatch):
    # Test run_strategy when metrics['IC'] is None and fallback is used
    def mock_last_metrics():
        return {"metrics": {"IC": None}, "equity_curve_path": None}

    def mock_run_bt_from_panel(panel_path=None, factor=None, horizon=None):
        return {"metrics": {"IC": 0.7}, "equity_curve_path": "curve2.png"}

    from app.ui_streamlit import run_strategy

    metrics, curve_path = run_strategy(mock_last_metrics, mock_run_bt_from_panel, "SENT_L1", 1, "dummy_path")
    assert metrics["IC"] == 0.7
    assert curve_path == "curve2.png"


def test_run_strategy_with_ic(monkeypatch):
    # Test run_strategy when metrics['IC'] is present
    def mock_last_metrics():
        return {"metrics": {"IC": 0.9}, "equity_curve_path": "curve3.png"}

    def mock_run_bt_from_panel(panel_path=None, factor=None, horizon=None):
        raise Exception("Should not be called")

    from app.ui_streamlit import run_strategy

    metrics, curve_path = run_strategy(mock_last_metrics, mock_run_bt_from_panel, "SENT_L1", 1, "dummy_path")
    assert metrics["IC"] == 0.9
    assert curve_path == "curve3.png"


def test_get_api_status_all_ok():
    from app.ui_streamlit import get_api_status

    # All APIs available
    status = get_api_status()
    assert status["sentiment"] is True or status["sentiment_err"] is None
    assert status["risk"] is True or status["risk_err"] is None
    assert status["strategy"] is True or status["strategy_err"] is None


def test_main_block_sentiment_error():
    from app.ui_streamlit import main_block

    result = main_block("sentiment", "sentiment error", None, None)
    assert "error" in result
    assert "Sentiment API not available" in result["error"]


def test_main_block_risk_error():
    from app.ui_streamlit import main_block

    result = main_block("risk", None, "risk error", None)
    assert "error" in result
    assert "Risk API not available" in result["error"]


def test_main_block_strategy_error():
    from app.ui_streamlit import main_block

    result = main_block("strategy", None, None, "strategy error")
    assert "error" in result
    assert "Strategy API not available" in result["error"]


def test_main_block_sentiment_ok():
    from app.ui_streamlit import main_block

    result = main_block("sentiment", None, None, None)
    assert result["sentiment"] is True


def test_main_block_risk_ok():
    from app.ui_streamlit import main_block

    result = main_block("risk", None, None, None)
    assert result["risk"] is True


def test_main_block_strategy_ok():
    from app.ui_streamlit import main_block

    result = main_block("strategy", None, None, None)
    assert result["strategy"] is True
