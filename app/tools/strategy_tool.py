def format_metrics(payload: dict) -> dict:
    """
    payload = {"metrics":{"IC":0.034,"Sharpe":0.72,"MaxDD":-0.11,"Turnover":0.45},
               "equity_curve_path":"reports/equity.png"}
    """
    return payload.get("metrics", {}), payload.get("equity_curve_path")
