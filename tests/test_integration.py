def test_imports() -> None:
    """
    Integration test to verify that required modules can be imported
    without errors.
    """
    import importlib

    importlib.import_module("market_sentiment_analyzer")
    importlib.import_module("risk_analysis_agent")
    importlib.import_module("strategy_simulator")
