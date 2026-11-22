"""Feasibility check: is the free transcript dataset good enough?

Downloads the Hugging Face dataset into data/raw/ (gitignored) and prints a
coverage report. Column names are NOT assumed: the script reports what it
finds and guesses date/ticker/text columns by name, so it works even if the
schema differs from the dataset card.

Usage:
    python scripts/01_inspect_dataset.py
    python scripts/01_inspect_dataset.py --dataset kurry/sp500_earnings_transcripts
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "data" / "results"

DATE_HINTS = ("date", "time", "timestamp")
TICKER_HINTS = ("ticker", "symbol")
TEXT_HINTS = ("transcript", "text", "content")


def guess(columns: list[str], hints: tuple[str, ...]) -> str | None:
    for hint in hints:
        for col in columns:
            if hint in col.lower():
                return col
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="kurry/sp500_earnings_transcripts")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(args.dataset, cache_dir=str(RAW / "hf_cache"))
    print(f"\nSplits: {list(ds.keys())}")
    df = pd.concat([ds[s].to_pandas() for s in ds], ignore_index=True)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}\n")
    print(df.dtypes, "\n")

    cols = list(df.columns)
    date_col = guess(cols, DATE_HINTS)
    ticker_col = guess(cols, TICKER_HINTS)
    text_col = guess(cols, TEXT_HINTS)
    print(f"Guessed -> date: {date_col}, ticker: {ticker_col}, text: {text_col}\n")

    if date_col:
        dates = pd.to_datetime(df[date_col], errors="coerce", utc=True)
        print(f"Date range: {dates.min()} -> {dates.max()}")
        print(f"Unparseable dates: {dates.isna().sum():,}")
        has_time = (dates.dt.hour.fillna(0) + dates.dt.minute.fillna(0)).gt(0).mean()
        print(f"Share of rows with a non-midnight timestamp: {has_time:.1%}")
        per_year = dates.dt.year.value_counts().sort_index()
        print("\nCalls per year:\n", per_year.to_string())
        per_year.to_csv(RESULTS / "calls_per_year.csv", header=["calls"])

    if ticker_col:
        print(f"\nDistinct tickers: {df[ticker_col].nunique():,}")

    if text_col:
        lengths = df[text_col].fillna("").str.split().str.len()
        print("\nTranscript length in words:")
        print(lengths.describe().round(0).to_string())
        short = (lengths < 2000).mean()
        print(f"Share under 2,000 words (possibly truncated): {short:.1%}")
        qa = df[text_col].fillna("").str.contains(
            r"question[- ]and[- ]answer|Q&A", case=False, regex=True
        )
        print(f"Share mentioning a Q&A section marker: {qa.mean():.1%}")

    print("\nMissing values per column:")
    print(df.isna().sum().to_string())


if __name__ == "__main__":
    main()
