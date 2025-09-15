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


def run_sentiment(msa_panel_stats, tickers, dfrom, dto, panel_path):
    symbols = [s.strip() for s in tickers.split(",") if s.strip()]
    payload = msa_panel_stats(symbols, dfrom, dto, panel_path=panel_path) if "panel_path" in msa_panel_stats.__code__.co_varnames else msa_panel_stats(symbols, dfrom, dto)
    stats = payload.get("stats", {})
    series = payload.get("series", [])
    img = _plot_sentiment(series)
    df = pd.DataFrame(series)
    return stats, img, df


def run_risk(risk_summarize, issuer, year, question, risk_data_dir=None):
    if risk_data_dir:
        os.environ["RISK_DATA_DIR"] = risk_data_dir
    payload = risk_summarize(issuer=issuer, year=int(year), question=question)
    summary = payload.get("summary", "(no summary)")
    categories = pd.DataFrame(payload.get("categories", []))
    sources = payload.get("sources", [])
    return summary, categories, sources


def run_strategy(strat_last_metrics, strat_run_bt_from_panel, factor, horizon, panel_path):
    res = strat_last_metrics()
    metrics = res.get("metrics", {}) or {}
    curve_path = res.get("equity_curve_path")
    if not metrics or metrics.get("IC") is None:
        res = (
            strat_run_bt_from_panel(panel_path=panel_path, factor=factor, horizon=int(horizon))
            if "panel_path" in strat_run_bt_from_panel.__code__.co_varnames
            else strat_run_bt_from_panel(factor=factor, horizon=int(horizon))
        )
        metrics = res.get("metrics", {})
        curve_path = res.get("equity_curve_path")
    return metrics, curve_path


def get_api_status():
    status = {
        "sentiment": SENT_ERR is None,
        "risk": RISK_ERR is None,
        "strategy": STRAT_ERR is None,
        "sentiment_err": SENT_ERR,
        "risk_err": RISK_ERR,
        "strategy_err": STRAT_ERR,
    }
    return status


def main_block(tool, SENT_ERR, RISK_ERR, STRAT_ERR):
    # Simulate the main block logic for testing
    result = {}
    if tool == "sentiment":
        if SENT_ERR:
            result["error"] = "Sentiment API not available. Check requirements/tags and reinstall."
        else:
            result["sentiment"] = True
    elif tool == "risk":
        if RISK_ERR:
            result["error"] = "Risk API not available. Check requirements/tags and reinstall."
        else:
            result["risk"] = True
    elif STRAT_ERR:
        result["error"] = "Strategy API not available. Check requirements/tags and reinstall."
    else:
        result["strategy"] = True
    return result


if go:
    tool, conf, reason = route_query(q, None if force == "Auto" else force)
    st.caption(f"Routing → **{tool}** (confidence {conf:.2f}). {reason}")

    if tool == "sentiment":
        if SENT_ERR:
            st.error("Sentiment API not available. Check requirements/tags and reinstall.")
        else:
            stats, img, df = run_sentiment(msa_panel_stats, tickers, dfrom, dto, PANEL_PATH)
            st.subheader("Sentiment")
            st.write(stats)
            if img:
                st.image(img)
            st.dataframe(df.head(200), use_container_width=True)

    elif tool == "risk":
        if RISK_ERR:
            st.error("Risk API not available. Check requirements/tags and reinstall.")
        else:
            summary, categories, sources = run_risk(risk_summarize, issuer, year, q, RISK_DATA_DIR)
            st.subheader("Risk Summary")
            st.write(summary)
            st.subheader("Categories")
            st.dataframe(categories, use_container_width=True)
            st.subheader("Sources")
            st.json(sources)

    elif STRAT_ERR:
        st.error("Strategy API not available. Check requirements/tags and reinstall.")
    else:
        metrics, curve_path = run_strategy(strat_last_metrics, strat_run_bt_from_panel, factor, horizon, STRAT_PANEL_PATH)
        st.subheader("Strategy Metrics")
        st.write(metrics)
        if curve_path and os.path.exists(curve_path):
            st.image(curve_path, caption="Equity Curve")
        else:
            st.info("No equity curve image found yet.")
