# Experiment log

Append-only record of every feature, variant, and horizon we try. Purpose: when
we eventually report a result, we can say how many things were tested to find it
(multiple-testing). Log candidates when they are *defined*, not only when they
look good. Never delete rows.

## Variants defined

| # | Date | Name | Definition | Status |
|---|------|------|------------|--------|
| 1 | 2026-11-22 | `lm_rates_negoff` | LM category rates (negative, positive, uncertainty, litigious, strong_modal, weak_modal, constraining) and net_tone; negated positives counted as negative (3-word window); `negate_negatives="off"` | defined, not yet evaluated |
| 2 | 2026-11-22 | `lm_rates_negdrop` | As #1 with `negate_negatives="drop"` | defined, not yet evaluated |
| 3 | 2026-11-22 | `lm_rates_negflip` | As #1 with `negate_negatives="flip"` | defined, not yet evaluated |

## Evaluation results

None yet. When we evaluate, record: variant #, sample (years, universe),
horizon, split scheme, metric (IC / decile spread / Sharpe), and whether costs
and survivorship caveats apply.

## Notes
- Negation rule and word-count method follow LM from memory; not yet verified
  against the SRAF documentation.
- Section splitting (`sections.py`) is an unverified heuristic until checked on real transcripts.
