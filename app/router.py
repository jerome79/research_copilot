# research_copilot/app/router.py

INTENT_RULES = [
    ("risk", ["risk", "10-k", "item 1a", "regulatory", "liquidity", "cybersecurity", "credit", "counterparty"]),
    ("sentiment", ["sentiment", "headline", "news", "tone", "positive", "negative"]),
    ("strategy", ["sharpe", "backtest", "ic", "returns", "equity curve", "performance", "alpha"]),
]


def route_query(q: str, override: str | None = None) -> tuple[str, float, str]:
    """
    Returns: (tool_name, confidence, reason)
    tool_name ∈ {"sentiment","risk","strategy"}
    """
    if override and override.lower() in {"sentiment", "risk", "strategy"}:
        return override.lower(), 1.0, f"Forced tool = {override}"

    ql = (q or "").lower()
    scores = {tool: 0 for tool, _ in INTENT_RULES}
    for tool, kws in INTENT_RULES:
        scores[tool] = sum(1 for kw in kws if kw in ql)

    tool = max(scores, key=lambda t: scores[t])
    nonzero = sum(1 for v in scores.values() if v > 0)
    conf = (scores[tool] / max(1, nonzero)) if nonzero else 0.0
    reason = f"Matched {scores[tool]} keywords for '{tool}'."
    return tool, conf, reason
