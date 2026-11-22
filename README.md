# Earnings-Call Sentiment Research

Side project in two studies, on **US large-cap companies only**:

1. **Tool comparison:** which sentiment tools (LM word lists, FinBERT, generic
   baseline, optionally a local LLM and a supervised model) best predict
   post-call abnormal returns?
2. **Alpha estimate:** using the best tool, how much alpha is there, how much
   survives in recent years, and how much after costs?

Mid- and small-cap universes were considered and dropped: free transcript data
for them is unlikely to exist, and survivorship/cost problems are worse there.

This is a **research exercise, not trading advice.** Results use free data with
known survivorship bias and should be read accordingly.

## Plan

1. **Feasibility** (`scripts/01_inspect_dataset.py`): check coverage, completeness
   and timestamps of the free transcript dataset.
2. **Prices**: pick a free source; measure how many delisted names are missing.
3. **Baseline**: Loughran-McDonald word-list features (Q&A vs prepared remarks,
   hedging, change vs the company's own history) -> event-study returns.
4. **Tool comparison (Study 1)**: add FinBERT, a generic baseline (e.g. VADER),
   a null baseline, and optionally a local LLM / supervised model. Compare on
   the *selection period only* by information coefficient, decile spread,
   incremental value over the earnings-surprise proxy, and stability.
5. **Freeze**: pick the winning tool, horizon and metric, record the choice in
   `docs/experiments.md`, then do not change it.
6. **Alpha (Study 2)**: evaluate the frozen tool on the untouched later period:
   decile long-short, costs, factor controls, decay over time, confidence intervals.
7. **Presentation**: static site (Next.js on Vercel) showing results. Later.

## Design rules

- No paid APIs. Heavy NLP runs locally or in CI, never in serverless functions.
- Trade only *after* the call ends (next open at the earliest) to avoid lookahead.
- Walk-forward validation only; log every feature and horizon tried.
- Select-then-freeze: choose the tool on an earlier period, measure alpha only
  on a later period that played no part in the choice (selection bias otherwise).
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

