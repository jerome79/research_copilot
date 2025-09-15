What it is: Orchestrator UI that routes queries to Sentiment, Risk, or Strategy services.

Why it matters: unifies research workflow; demos end-to-end product thinking.

Quick start:

Start servers in 3 terminals:

uvicorn servers.sentiment_server:app --port 8601 --reload

uvicorn servers.risk_server:app --port 8602 --reload

uvicorn servers.strategy_server:app --port 8603 --reload

Run copilot UI:

streamlit run app/ui_streamlit.py

Ask:

“Summarize AAPL 2023 risks with citations”

“Show sentiment trend for NVDA 2024-01-01..2024-12-31”

“Sharpe and IC for sentiment last year”

Roadmap: swap HTTP for MCP transport; containerize; add LLM router (LangGraph) and a “Research Notebook” exporter.

“How this integrates with my other repos” section:

“This UI imports three versioned packages from GitHub:

market-sentiment-analyzer → sentiment stats

risk-analysis-agent → RAG + risk classification

strategy-simulator → metrics/equity curve
All are pinned in requirements.txt to reproducible tags.”
