INTENT_RULES = [
    ("risk", ["risk", "10-k", "item 1a", "regulatory", "liquidity", "cybersecurity"]),
    ("sentiment", ["sentiment", "headline", "news", "tone"]),
    ("strategy", ["sharpe", "backtest", "IC", "returns", "equity curve", "performance"]),
]

def route_query(q: str, override: str | None = None) -> tuple[str, float, str]:
    if override and override.lower() in {"sentiment","risk","strategy"}:
        return override.lower(), 1.0, f"Forced tool = {override}"
    ql = q.lower()
    scores = {}
    for tool, kws in INTENT_RULES:
        scores[tool] = sum(k in ql for k in kws)
    tool = max(scores, key=scores.get)
    conf = scores[tool] / max(1, len([k for k in INTENT_RULES if scores[k] > 0]))
    reason = f"Matched keywords for {tool}: {scores[tool]}"
    return tool, conf, reason
