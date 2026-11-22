# Earnings-Call Sentiment Research

Side project: do sentiment features from earnings-call transcripts predict
post-call abnormal returns, and how much of any effect survives in recent years
and after costs?

This is a **research exercise, not trading advice.** Results use free data with
known survivorship bias and should be read accordingly.

## Plan

1. **Feasibility** (`scripts/01_inspect_dataset.py`): check coverage, completeness
   and timestamps of the free transcript dataset.
2. **Prices**: pick a free source; measure how many delisted names are missing.
3. **Baseline**: Loughran-McDonald word-list features (Q&A vs prepared remarks,
   hedging, change vs the company's own history) -> event-study returns.
4. **Evaluation**: walk-forward splits, information coefficient, decile long-short,
   costs, factor controls. Report decay over time.
5. **Upgrade**: FinBERT or a local open LLM as extra features; compare to baseline.
6. **Presentation**: static site (Next.js on Vercel) showing results. Later.

## Design rules

- No paid APIs. Heavy NLP runs locally or in CI, never in serverless functions.
- Trade only *after* the call ends (next open at the earliest) to avoid lookahead.
- Walk-forward validation only; log every feature and horizon tried.
- Controls: market/sector-adjusted returns; earnings-surprise proxy.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/01_inspect_dataset.py
```

Data lands in `data/raw/` (gitignored). Small result tables go in `data/results/`.

## Layout

```
src/earnings_alpha/   library code
scripts/              numbered, runnable pipeline steps
data/raw|interim|results/
```

