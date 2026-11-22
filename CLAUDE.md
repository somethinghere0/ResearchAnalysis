# CLAUDE.md

Side project: test whether earnings-call sentiment features predict post-call
abnormal returns (US stocks). Research exercise, not trading advice. See
README.md for the plan.

## Hard rules
- No paid APIs (including the Claude API). Free data and free/local models only.
- Heavy NLP (FinBERT, open LLMs) runs locally or in CI, never in serverless functions.
- US equities only.
- No lookahead: trade only after the call ends (next open at the earliest).
- Walk-forward validation only; log every feature/horizon tried (multiple-testing).
- Control for earnings surprise (use announcement-window return as proxy if no consensus data).
- Always label results as survivorship-biased when the data is, and never present them as tradable.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
- Feasibility check: `python scripts/01_inspect_dataset.py`
- Tests: `pytest`

## Conventions
- Pipeline steps are numbered scripts in `scripts/`; reusable code goes in `src/earnings_alpha/`.
- `data/raw/` and `data/interim/` are gitignored. Only small tables in `data/results/` get committed.
- Numbers come from code, never from an LLM. Models score language only.

## Status
- Scaffold created. Feasibility check (`01_inspect_dataset.py`) not yet run.
- LM scoring (`lexicon.py`) implemented and tested on the real dictionary
  (`data/raw/lm_master_dictionary.csv`, user-downloaded); not yet run on real transcripts.
- Log every feature variant in `docs/experiments.md` when it is defined.
- Web frontend (Next.js on Vercel) is deferred until there is a signal worth showing.
