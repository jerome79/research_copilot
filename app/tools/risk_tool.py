import pandas as pd

def render_risk_result(payload: dict) -> tuple[str, pd.DataFrame, list]:
    """
    payload = {
      "issuer":"AAPL","year":2023,
      "summary":"...",
      "categories":[{"label":"Cybersecurity","confidence":0.82}, ...],
      "sources":[{"path":".../item_1a.txt","chunk_id":"..."}]
    }
    """
    summary = payload.get("summary","(no summary)")
    cats = pd.DataFrame(payload.get("categories", []))
    sources = payload.get("sources", [])
    return summary, cats, sources
