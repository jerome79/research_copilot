import streamlit as st, os
from dotenv import load_dotenv
from app.router import route_query
from app.mcp_client import MCPClient
from app.tools.sentiment_tool import render_sentiment_result
from app.tools.risk_tool import render_risk_result
from app.tools.strategy_tool import format_metrics

load_dotenv()
st.set_page_config(page_title="Research Copilot", layout="wide")
st.title("🧭 Research Copilot")

client = MCPClient()

with st.sidebar:
    st.header("Query")
    q = st.text_area("Ask a question", "What are NVDA 2023 risks and how did sentiment perform last quarter?")
    force = st.selectbox("Force tool (optional)", ["Auto","Sentiment","Risk","Strategy"])
    tickers = st.text_input("Tickers (comma)", os.getenv("DEFAULT_TICKERS","AAPL,MSFT,NVDA"))
    dfrom = st.text_input("From", os.getenv("DEFAULT_DATE_FROM","2024-01-01"))
    dto   = st.text_input("To", os.getenv("DEFAULT_DATE_TO","2024-12-31"))
    issuer = st.text_input("Issuer (risk)", "AAPL")
    year   = st.number_input("Year (risk)", 2023, 2030, 2023)
    go = st.button("Run")

if go:
    tool, conf, reason = route_query(q, None if force=="Auto" else force)
    st.caption(f"Routing → **{tool}** (confidence {conf:.2f}). Reason: {reason}")

    if tool == "sentiment":
        symbols = [s.strip() for s in tickers.split(",") if s.strip()]
        payload = client.sentiment_panel_stats(symbols, dfrom, dto)
        df, buf = render_sentiment_result(payload)
        st.subheader("Sentiment")
        st.write(payload.get("stats", {}))
        st.dataframe(df.head(50), use_container_width=True)
        if buf:
            st.image(buf)

    elif tool == "risk":
        payload = client.risk_summarize(issuer, int(year), q)
        summary, cats, sources = render_risk_result(payload)
        st.subheader("Risk Summary")
        st.write(summary)
        st.subheader("Categories")
        st.dataframe(cats, use_container_width=True)
        st.subheader("Sources")
        st.json(sources)

    else:  # strategy
        # Try last metrics first; fallback to run_backtest
        try:
            payload = client.strategy_last_metrics()
        except Exception:
            payload = client.strategy_run_backtest("SENT_L1", 1, "SP500", 10)
        metrics, curve = format_metrics(payload)
        st.subheader("Strategy Metrics")
        st.write(metrics)
        if curve and os.path.exists(curve):
            st.image(curve, caption="Equity Curve")
        else:
            st.info("No equity curve image found.")
