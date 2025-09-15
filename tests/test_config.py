# test_config.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import S, _abs, validate_paths


def test_settings_defaults() -> None:
    """
    Test that default settings in S are set correctly.
    """
    assert S.DEFAULT_TICKERS == "AAPL,MSFT,NVDA"
    assert S.DEFAULT_DATE_FROM == "2024-01-01"
    assert S.STRAT_DEFAULT_FACTOR == "SENT_L1"


def test_validate_paths_handles_missing() -> None:
    """
    Test path validation returns a list of messages.
    """
    msgs = validate_paths()
    assert isinstance(msgs, list)


def test_abs_none() -> None:
    """
    Test that _abs returns None when given None.
    """
    assert _abs(None) is None


def test_abs_valid() -> None:
    """
        Test that _abs returns an absolute path for a valid relative path.
    :return:
    """
    p = _abs(".")
    assert isinstance(p, str)
    assert Path(p).exists()


def test_validate_paths_missing(monkeypatch) -> None:
    """
    Test that validate_paths detects missing files/dirs when paths are set to non-existent values.
    """
    monkeypatch.setattr(S, "SENTIMENT_PANEL_PATH", "missing_file.parquet")
    monkeypatch.setattr(S, "STRAT_REPORT_DIR", "missing_dir")
    msgs = validate_paths()
    assert any("not found" in m or "missing" in m for m in msgs)
