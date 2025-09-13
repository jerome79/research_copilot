import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

def render_sentiment_result(payload: dict) -> tuple[pd.DataFrame, BytesIO]:
    """
    payload = {
      "stats": {"avg_sentiment": ..., "n_news": ...},
      "series": [{"date":"2024-01-02","ticker":"AAPL","avg_sentiment":0.12}, ...]
    }
    """
    df = pd.DataFrame(payload.get("series", []))
    buf = BytesIO()
    if not df.empty:
        fig, ax = plt.subplots(figsize=(7,3))
        for t, g in df.groupby("ticker"):
            g = g.sort_values("date")
            ax.plot(pd.to_datetime(g["date"]), g["avg_sentiment"], label=t)
        ax.set_title("Daily Sentiment Trend")
        ax.set_ylabel("avg_sentiment")
        ax.grid(True); ax.legend(loc="upper left", ncol=3, fontsize=8)
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=120)
        buf.seek(0)
    return df, buf
