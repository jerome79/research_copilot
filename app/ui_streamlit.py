# research_copilot/app/ui_streamlit.py
import os
import sys
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ---- Load env ----
load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.router import route_query

# ---- Import public APIs from your three repos ----
# Make sure Copilot venv has installed them from GitHub:
# pip install -r requirements.txt  (with git+https://... lines)
SENT_ERR: str | None = None
RISK_ERR: str | None = None
STRAT_ERR: str | None = None
try:
    from market_sentiment_analyzer.public_api import panel_stats as msa_panel_stats
except Exception as e:
    msa_panel_stats = None
    SENT_ERR = f"Sentiment API import failed: {e}"

try:
    from risk_analysis_agent.public_api import summarize_risk as risk_summarize
except Exception as e:
    risk_summarize = None
    RISK_ERR = f"Risk API import failed: {e}"

try:
    # adjust the path if your module lives under a different root (src/public_api, app/public_api, etc.)
    from strategy_simulator.public_api import last_metrics as strat_last_metrics, run_backtest_from_panel as strat_run_bt_from_panel
except Exception as e:
    strat_last_metrics = None
    strat_run_bt_from_panel = None
    STRAT_ERR = f"Strategy API import failed: {e}"


# ---- Config / defaults from .env ----
PANEL_PATH = os.getenv("SENTIMENT_PANEL_PATH", "../market-sentiment-analyzer/data/sentiment_panel.parquet")
DEF_TICKERS = os.getenv("DEFAULT_TICKERS", "AAPL,MSFT,NVDA")
DEF_FROM = os.getenv("DEFAULT_DATE_FROM", "2024-01-01")
DEF_TO = os.getenv("DEFAULT_DATE_TO", "2024-12-31")

RISK_DEF_ISS = os.getenv("RISK_DEFAULT_ISSUER", "AAPL")
RISK_DEF_YR = int(os.getenv("RISK_DEFAULT_YEAR", "2023"))
RISK_DATA_DIR = os.getenv("RISK_DATA_DIR")  # optional, only if your API uses it

STRAT_PANEL_PATH = os.getenv("STRAT_SENTIMENT_PANEL_PATH", PANEL_PATH)
STRAT_DEF_FACTOR = os.getenv("STRAT_DEFAULT_FACTOR", "SENT_L1")
STRAT_DEF_HORIZ = int(os.getenv("STRAT_DEFAULT_HORIZON", "1"))

# ---- Page ----
st.set_page_config(page_title="🧭 Research Copilot", layout="wide")
st.title("🧭 Research Copilot")

# Health hints
cols = st.columns(3)
cols[0].markdown("✅ **Sentiment API** ready" if not SENT_ERR else f"⚠️ **Sentiment API**: {SENT_ERR}")
cols[1].markdown("✅ **Risk API** ready" if not RISK_ERR else f"⚠️ **Risk API**: {RISK_ERR}")
cols[2].markdown("✅ **Strategy API** ready" if not STRAT_ERR else f"⚠️ **Strategy API**: {STRAT_ERR}")

with st.sidebar:
    st.header("Query")
    q = st.text_area("Ask a question", "What are NVDA 2023 risks and how did sentiment perform last quarter?")
    force = st.selectbox("Force tool (optional)", ["Auto", "Sentiment", "Risk", "Strategy"])
    st.divider()
    st.caption("Sentiment inputs")
    tickers = st.text_input("Tickers (comma)", DEF_TICKERS)
    dfrom = st.text_input("From", DEF_FROM)
    dto = st.text_input("To", DEF_TO)
    st.caption("Risk inputs")
    issuer = st.text_input("Issuer", RISK_DEF_ISS)
    year = st.number_input("Year", min_value=2000, max_value=2100, value=RISK_DEF_YR, step=1)
    st.caption("Strategy inputs")
    factor = st.text_input("Factor", STRAT_DEF_FACTOR)
    horizon = st.number_input("Horizon (days)", min_value=1, max_value=20, value=STRAT_DEF_HORIZ, step=1)
    go = st.button("Run")


def _plot_sentiment(series_records: list[dict]) -> BytesIO | None:
    df = pd.DataFrame(series_records)
    if df.empty:
        return None
    buf = BytesIO()
    fig, ax = plt.subplots(figsize=(7, 3))
    for t, g in df.groupby("ticker"):
        tmp = g.sort_values("date")
        ax.plot(pd.to_datetime(g["date"]), tmp["avg_sentiment"], label=t)
    ax.set_title("Daily Sentiment Trend")
    ax.set_ylabel("avg_sentiment")
    ax.grid(True)
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    return buf


if go:
    tool, conf, reason = route_query(q, None if force == "Auto" else force)
    st.caption(f"Routing → **{tool}** (confidence {conf:.2f}). {reason}")

    if tool == "sentiment":
        if SENT_ERR:
            st.error("Sentiment API not available. Check requirements/tags and reinstall.")
        else:
            symbols = [s.strip() for s in tickers.split(",") if s.strip()]
            # Call your installed public API
            payload = (
                msa_panel_stats(symbols, dfrom, dto, panel_path=PANEL_PATH) if "panel_path" in msa_panel_stats.__code__.co_varnames else msa_panel_stats(symbols, dfrom, dto)
            )
            st.subheader("Sentiment")
            st.write(payload.get("stats", {}))
            img = _plot_sentiment(payload.get("series", []))
            if img:
                st.image(img)
            st.dataframe(pd.DataFrame(payload.get("series", [])).head(200), use_container_width=True)

    elif tool == "risk":
        if RISK_ERR:
            st.error("Risk API not available. Check requirements/tags and reinstall.")
        else:
            # If your risk public_api uses RISK_DATA_DIR, set it globally beforehand
            if RISK_DATA_DIR:
                os.environ["RISK_DATA_DIR"] = RISK_DATA_DIR
            payload = risk_summarize(issuer=issuer, year=int(year), question=q)
            st.subheader("Risk Summary")
            st.write(payload.get("summary", "(no summary)"))
            st.subheader("Categories")
            st.dataframe(pd.DataFrame(payload.get("categories", [])), use_container_width=True)
            st.subheader("Sources")
            st.json(payload.get("sources", []))

    elif STRAT_ERR:
        st.error("Strategy API not available. Check requirements/tags and reinstall.")
    else:
        st.subheader("Strategy Metrics")
        # Try last_metrics first; if empty, run a quick backtest from panel
        res = strat_last_metrics()
        metrics = res.get("metrics", {}) or {}
        curve_path = res.get("equity_curve_path")
        if not metrics or metrics.get("IC") is None:
            res = (
                strat_run_bt_from_panel(panel_path=STRAT_PANEL_PATH, factor=factor, horizon=int(horizon))
                if "panel_path" in strat_run_bt_from_panel.__code__.co_varnames
                else strat_run_bt_from_panel(factor=factor, horizon=int(horizon))
            )
            metrics = res.get("metrics", {})
            curve_path = res.get("equity_curve_path")
        st.write(metrics)
        if curve_path and os.path.exists(curve_path):
            st.image(curve_path, caption="Equity Curve")
        else:
            st.info("No equity curve image found yet.")
