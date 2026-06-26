#!/usr/bin/env python3
"""
CSE Daily Price Collector
=========================
Downloads daily OHLCV bars for all Colombo Stock Exchange (CSE) equities
and the All Share Price Index (ASPI) from TradingView's data feed.

Data source
-----------
TradingView's real-time WebSocket feed (exchange code: CSELK).  The
tvDatafeed library handles authentication and the WebSocket handshake.
An anonymous session (no credentials) works for short histories; a free
TradingView account unlocks the full available history per symbol.

Set TV_USERNAME and TV_PASSWORD environment variables for an authenticated
session, or pass --username / --password on the command line.

Output
------
  data/stock_prices.csv   one row per (symbol, trading day)
                          columns: symbol, date, open, high, low, close, volume

  data/aspi.csv           one row per trading day for the All Share Price Index
                          columns: date, open, high, low, close, volume
                          Volume is always blank — TradingView carries no volume
                          for this index.

Both files match the column layout of the reference dataset in
../New project/*.csv and can be used as direct replacements or extensions.

Reference dataset coverage
--------------------------
The sample CSVs in ../New project/ cover 2025-02-03 to 2026-02-27
(~277 CSE trading sessions, roughly one calendar year).  With the default
--n-bars 500 (≈ 2 years), a fresh run will extend that range forward to
the current date and reach back further into 2024.

Resuming an interrupted run
---------------------------
After each symbol the script updates data/status.json.  Re-running picks
up where it stopped.  Pass --fresh to discard the saved state and restart.

Usage
-----
  python collect.py                              # 500 bars, anonymous session
  python collect.py --n-bars 400                 # ≈ 400 trading days ending today
  python collect.py --from-date 2025-02-03       # infer bar count from a start date
  python collect.py --fresh                      # restart, ignore saved progress
  python collect.py --username user@mail.com --password secret
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    sys.exit(
        "tvDatafeed is not installed.\n"
        "  pip install tvDatafeed\n"
    )

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE        = Path(__file__).resolve().parent
COMPANY_MAP = HERE / "company_mapping.json"
DATA_DIR    = HERE / "data"
STATUS_FILE  = DATA_DIR / "status.json"
STOCK_CSV    = DATA_DIR / "stock_prices.csv"
ASPI_CSV     = DATA_DIR / "aspi.csv"

# ---------------------------------------------------------------------------
# Source settings
# ---------------------------------------------------------------------------

EXCHANGE    = "CSELK"

# TradingView ticker for the All Share Price Index.
# If this returns no data, try: "ASPI", "SRALLSH"
ASPI_SYMBOL = "CSEALL"

# ---------------------------------------------------------------------------
# Operational defaults
# ---------------------------------------------------------------------------

DEFAULT_N_BARS = 500    # ≈ 2 years of CSE trading days

# Conservative pacing — TradingView's feed silently returns empty responses
# when it receives requests faster than it can serve them.
REQUEST_DELAY_S = 1.2
MAX_RETRIES     = 3
RETRY_DELAY_S   = 6.0   # multiplied by attempt number on each retry

# ---------------------------------------------------------------------------
# Symbol loading
# ---------------------------------------------------------------------------

def load_symbols() -> dict:
    """
    Return {ticker: company_name} for every symbol in company_mapping.json.

    Keys in the mapping look like "CSELK-ABAN.N0000"; the exchange prefix
    is stripped here because tvDatafeed takes exchange and symbol separately.
    """
    with open(COMPANY_MAP) as f:
        raw = json.load(f)
    return {k.split("-", 1)[1]: v for k, v in raw.items()}

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def load_status() -> dict:
    """Read the saved session state, or return an empty default."""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"aspi_done": False, "completed_symbols": []}


def save_status(status: dict) -> None:
    status["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

# ---------------------------------------------------------------------------
# Bar count helpers
# ---------------------------------------------------------------------------

def n_bars_from_date(from_date_str: str) -> int:
    """
    Estimate the number of daily bars between from_date and today.

    CSE trades Monday–Friday minus public holidays.  We approximate as
    (calendar days × 5/7) and add a 25-bar buffer so the collected range
    always covers the requested start date even in holiday-heavy periods.
    """
    start_d = date.fromisoformat(from_date_str)
    cal_days = (date.today() - start_d).days
    return max(int(cal_days * 5 / 7) + 25, 1)

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_with_retry(tv: TvDatafeed, symbol: str, n_bars: int):
    """
    Fetch n_bars daily bars for symbol on EXCHANGE.

    Returns a DataFrame on success, None if all attempts fail.
    Each retry waits RETRY_DELAY_S × attempt_number seconds so that
    transient feed overloads have time to clear.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = tv.get_hist(symbol, EXCHANGE, interval=Interval.in_daily, n_bars=n_bars)
            if df is not None and not df.empty:
                return df
            print(f"    attempt {attempt}: empty response")
        except Exception as exc:
            print(f"    attempt {attempt}: {exc}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_S * attempt)
    return None

# ---------------------------------------------------------------------------
# Data formatting
# ---------------------------------------------------------------------------

def _fmt(val) -> str:
    """
    Format a numeric OHLCV field as a float string.

    Python's default float repr gives "468.0" for clean integers and
    "440.75" for fractional values, which matches the reference CSV format.
    """
    return str(float(val))


def _vol(raw) -> str:
    """
    Return the volume as a float string, or an empty string for NaN / zero.

    TradingView stores missing volume as 0.0 or NaN depending on the
    symbol type.  Both are treated as absent data.
    """
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return ""
    # NaN is the only float not equal to itself
    if v != v or v == 0.0:
        return ""
    return str(v)


def df_to_rows(df, symbol: str = None) -> list:
    """
    Convert a tvDatafeed DataFrame into plain CSV rows.

    symbol=None  →  [date, open, high, low, close, volume]       (ASPI)
    symbol="XYZ" →  [symbol, date, open, high, low, close, volume]  (stocks)

    For ASPI, volume is always blank regardless of what the feed returns —
    the reference dataset confirms the index carries no traded volume.
    Dates are formatted as YYYY-MM-DD strings.
    """
    is_index = symbol is None
    rows = []
    for ts, row in df.iterrows():
        date_str = ts.strftime("%Y-%m-%d")
        o = _fmt(row["open"])
        h = _fmt(row["high"])
        l = _fmt(row["low"])
        c = _fmt(row["close"])
        v = "" if is_index else _vol(row.get("volume", 0))

        if symbol:
            rows.append([symbol, date_str, o, h, l, c, v])
        else:
            rows.append([date_str, o, h, l, c, v])
    return rows

# ---------------------------------------------------------------------------
# Collection routines
# ---------------------------------------------------------------------------

def collect_aspi(tv: TvDatafeed, n_bars: int) -> bool:
    """
    Fetch ASPI daily bars and write data/aspi.csv.

    Overwrites any existing ASPI file — the ASPI is a single series so
    a fresh fetch is always the complete and correct dataset.
    Returns True on success.
    """
    print(f"Collecting ASPI  ({ASPI_SYMBOL} on {EXCHANGE})...")
    df = fetch_with_retry(tv, ASPI_SYMBOL, n_bars)
    if df is None:
        print(
            f"  Failed to fetch ASPI.\n"
            f"  If '{ASPI_SYMBOL}' is wrong, edit ASPI_SYMBOL in this file.\n"
            f"  Alternatives to try: 'ASPI', 'SRALLSH'"
        )
        return False

    rows = df_to_rows(df, symbol=None)
    with open(ASPI_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        w.writerows(rows)

    print(f"  {len(rows)} bars  →  {ASPI_CSV.relative_to(HERE)}")
    return True


def collect_stocks(tv: TvDatafeed, symbols: dict, n_bars: int, completed: list) -> list:
    """
    Fetch daily OHLCV for each symbol and append to data/stock_prices.csv.

    Symbols already in `completed` are skipped so the function is safe to
    call after an interrupted run — pass the completed list from status.json.
    The file is flushed after every symbol so a mid-run kill loses at most
    one symbol's worth of data.

    Returns the updated completed list.
    """
    remaining = [s for s in symbols if s not in completed]
    total     = len(symbols)

    # Write the header only when starting fresh.  On resume the file already
    # contains it; writing again would corrupt the CSV.
    if not STOCK_CSV.exists() or not completed:
        with open(STOCK_CSV, "w", newline="") as f:
            csv.writer(f).writerow(["symbol", "date", "open", "high", "low", "close", "volume"])

    with open(STOCK_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        for symbol in remaining:
            idx = len(completed) + 1
            print(f"  [{idx}/{total}]  {symbol:<16}", end=" ", flush=True)

            df = fetch_with_retry(tv, symbol, n_bars)
            if df is None:
                print("no data")
                completed.append(symbol)
                continue

            rows = df_to_rows(df, symbol=symbol)
            writer.writerows(rows)
            f.flush()
            completed.append(symbol)
            print(f"{len(rows)} bars")
            time.sleep(REQUEST_DELAY_S)

    return completed

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Download CSE daily OHLCV data from TradingView.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python collect.py\n"
            "  python collect.py --from-date 2024-01-01\n"
            "  python collect.py --n-bars 400 --fresh\n"
            "  python collect.py --username user@mail.com --password secret\n"
        ),
    )
    p.add_argument(
        "--n-bars", type=int, default=DEFAULT_N_BARS, metavar="N",
        help=f"daily bars to request per symbol (default: {DEFAULT_N_BARS} ≈ 2 years)",
    )
    p.add_argument(
        "--from-date", metavar="YYYY-MM-DD",
        help="derive bar count from a start date; overrides --n-bars",
    )
    p.add_argument(
        "--fresh", action="store_true",
        help="discard saved session state and restart from the beginning",
    )
    p.add_argument(
        "--username", default=os.environ.get("TV_USERNAME"),
        help="TradingView username (or set TV_USERNAME env var)",
    )
    p.add_argument(
        "--password", default=os.environ.get("TV_PASSWORD"),
        help="TradingView password (or set TV_PASSWORD env var)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    n_bars = n_bars_from_date(args.from_date) if args.from_date else args.n_bars

    symbols = load_symbols()
    print(f"Loaded {len(symbols)} symbols from company_mapping.json")
    print(f"Requesting {n_bars} bars per symbol  (~{n_bars // 250} year(s) of data)\n")

    status = {"aspi_done": False, "completed_symbols": []}
    if not args.fresh:
        saved = load_status()
        done = len(saved.get("completed_symbols", []))
        if done:
            print(f"Resuming: {done}/{len(symbols)} symbols already in status.json\n")
        status = saved

    # Authenticated sessions return more historical bars on some symbols.
    tv = TvDatafeed(
        username=args.username,
        password=args.password,
    )

    # --- ASPI ---
    if not status.get("aspi_done"):
        status["aspi_done"] = collect_aspi(tv, n_bars)
        save_status(status)
    else:
        print("ASPI: already collected, skipping")
    print()

    # --- Equities ---
    status["completed_symbols"] = collect_stocks(
        tv,
        symbols,
        n_bars,
        list(status.get("completed_symbols", [])),
    )
    save_status(status)

    n_done = len([s for s in status["completed_symbols"] if s in symbols])
    print(f"\nFinished: {n_done}/{len(symbols)} symbols collected.")
    if n_done < len(symbols):
        print("Re-run to collect any symbols that failed.")
    print(f"Output:  {STOCK_CSV.relative_to(HERE)}")
    print(f"         {ASPI_CSV.relative_to(HERE)}")


if __name__ == "__main__":
    main()
