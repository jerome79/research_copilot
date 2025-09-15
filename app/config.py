import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _abs(p: str | None) -> str | None:
    if not p:
        return None
    return str(Path(p).expanduser().resolve())


class Settings:
    SENTIMENT_PANEL_PATH = _abs(os.getenv("SENTIMENT_PANEL_PATH", "samples/sentiment_panel.sample.parquet"))
    DEFAULT_TICKERS = os.getenv("DEFAULT_TICKERS", "AAPL,MSFT,NVDA")
    DEFAULT_DATE_FROM = os.getenv("DEFAULT_DATE_FROM", "2024-01-01")
    DEFAULT_DATE_TO = os.getenv("DEFAULT_DATE_TO", "2024-12-31")

    RISK_DATA_DIR = _abs(os.getenv("RISK_DATA_DIR"))
    RISK_DEFAULT_ISSUER = os.getenv("RISK_DEFAULT_ISSUER", "AAPL")
    RISK_DEFAULT_YEAR = int(os.getenv("RISK_DEFAULT_YEAR", "2023"))

    STRAT_REPORT_DIR = _abs(os.getenv("STRAT_REPORT_DIR", "samples/strategy_reports"))
    STRAT_PANEL_PATH = _abs(os.getenv("STRAT_SENTIMENT_PANEL_PATH", SENTIMENT_PANEL_PATH))
    STRAT_DEFAULT_FACTOR = os.getenv("STRAT_DEFAULT_FACTOR", "SENT_L1")
    STRAT_DEFAULT_HORIZON = int(os.getenv("STRAT_DEFAULT_HORIZON", "1"))


S = Settings()


def validate_paths() -> list[str]:
    msgs = []
    if not S.SENTIMENT_PANEL_PATH or not Path(S.SENTIMENT_PANEL_PATH).exists():
        msgs.append(f"⚠️ SENTIMENT_PANEL_PATH not found: {S.SENTIMENT_PANEL_PATH}")
    if S.STRAT_REPORT_DIR and not Path(S.STRAT_REPORT_DIR).exists():
        msgs.append(f"⚠️STRAT_REPORT_DIR missing: {S.STRAT_REPORT_DIR} (created by strategy runs)")
    return msgs
