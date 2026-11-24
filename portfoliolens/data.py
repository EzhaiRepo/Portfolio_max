"""Explicit synthetic fixture and opt-in market-price download."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .engine import validate_prices


def demo_prices():
    """Fixed-seed synthetic business-day paths; never historical market prices."""
    rng = np.random.default_rng(5540)
    dates = pd.bdate_range("2022-01-03", periods=1009)
    market = rng.normal(0.00025, 0.010, len(dates) - 1)
    shocks = rng.normal(size=(len(dates) - 1, 3))
    stock = market[:, None] * np.array([1.2, 1.0, 0.4]) + shocks * [0.018, 0.012, 0.008]
    stock += np.array([0.00015, 0.00010, 0.00005])
    daily = np.column_stack([stock, market])
    values = 100 * np.vstack([np.ones(4), np.cumprod(1 + daily, axis=0)])
    return pd.DataFrame(values, index=dates, columns=["AVGO", "ETN", "PGR", "SPY"])


def read_prices(path):
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    validate_prices(frame)
    return frame


def read_holdings(path):
    frame = pd.read_csv(path, dtype={"ticker": str})
    if set(frame.columns) != {"ticker", "weight"} or frame.ticker.isna().any():
        raise ValueError("Holdings CSV must have exactly ticker,weight columns")
    frame.ticker = frame.ticker.str.strip().str.upper()
    if frame.ticker.duplicated().any() or frame.ticker.eq("").any():
        raise ValueError("Holdings tickers must be unique and nonempty")
    return dict(zip(frame.ticker, pd.to_numeric(frame.weight, errors="raise")))


def fingerprint(prices):
    return hashlib.sha256(prices.to_csv(date_format="%Y-%m-%d").encode()).hexdigest()


def download_prices(tickers, start, end, output):
    import yfinance as yf
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(output.parent / ".cache"))
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if raw is None or raw.empty:
        raise ValueError("Market download returned no prices; use --demo for an offline run")
    prices = raw["Close"].copy()
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(tickers[0])
    prices = prices.reindex(columns=tickers)
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    validate_prices(prices)  # fail on missing history instead of deleting dates silently
    prices.to_csv(output, index_label="date")
    metadata = {"source": "Yahoo Finance via yfinance; auto_adjust=True", "tickers": tickers,
                "start_inclusive": start, "end_exclusive": end,
                "retrieved_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "csv_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "note": "Vendor-adjusted price proxy; revisions and historical universe bias remain."}
    output.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return prices
