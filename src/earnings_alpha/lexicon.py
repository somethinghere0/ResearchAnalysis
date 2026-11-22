"""Loughran-McDonald (LM) word-list features.

The LM master dictionary is a CSV with one row per word and one column per
category; a category cell is 0 if the word is not in it, otherwise the year it
was added. Download it yourself from the Notre Dame SRAF site and save it as
data/raw/lm_master_dictionary.csv (check the licence terms there first).

Features are counts per category divided by total word count, so calls of
different lengths are comparable.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

CATEGORIES = (
    "negative",
    "positive",
    "uncertainty",
    "litigious",
    "strong_modal",
    "weak_modal",
    "constraining",
)

# LM recommend treating a positive word as negated when one of these appears
# within the three preceding words.
NEGATIONS = frozenset(
    {"no", "not", "none", "neither", "never", "nobody", "nothing", "n't", "cannot"}
)

_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def _norm(name: str) -> str:
    return re.sub(r"[^a-z]", "_", name.strip().lower()).strip("_")


def load_dictionary(path: str | Path) -> dict[str, set[str]]:
    """Return {category: {UPPERCASE words}} from the LM master dictionary CSV."""
    df = pd.read_csv(path)
    df.columns = [_norm(c) for c in df.columns]
    if "word" not in df.columns:
        raise ValueError(f"No 'Word' column in {path}; found {list(df.columns)}")
    words = df["word"].astype(str).str.upper()
    out: dict[str, set[str]] = {}
    for cat in CATEGORIES:
        if cat not in df.columns:
            raise ValueError(f"Category column '{cat}' missing from {path}")
        out[cat] = set(words[df[cat] != 0])
    return out


def tokenize(text: str) -> list[str]:
    return [t.upper() for t in _TOKEN_RE.findall(text or "")]


def _is_negated(tokens: list[str], i: int) -> bool:
    window = tokens[max(0, i - 3) : i]
    return any(w in {n.upper() for n in NEGATIONS} for w in window)


NEGATE_NEGATIVES_MODES = ("off", "drop", "flip")


def score_text(
    text: str,
    lexicon: dict[str, set[str]],
    negate_negatives: str = "off",
) -> dict[str, float]:
    """Per-category rates plus summary scores for one block of text.

    Returns n_words, one `<category>_rate` per category, and
    net_tone = (positive - negative) / n_words.

    Negated positive words are always counted as negative (LM's guidance).
    `negate_negatives` controls our own extension for negated negative words
    (a negation within the 3 preceding words):
      - "off":  no special handling; the published LM behaviour (default).
      - "drop": the word is not counted as negative (and not as positive).
      - "flip": the word is counted as positive.
    Only the negative/positive counts are affected; other categories are
    unchanged.
    """
    if negate_negatives not in NEGATE_NEGATIVES_MODES:
        raise ValueError(
            f"negate_negatives must be one of {NEGATE_NEGATIVES_MODES}, "
            f"got {negate_negatives!r}"
        )
    tokens = tokenize(text)
    n = len(tokens)
    counts = {cat: 0 for cat in CATEGORIES}
    negated_positive = 0
    flipped_negative = 0
    for i, tok in enumerate(tokens):
        negated = None  # computed lazily; only positive/negative words need it
        for cat in CATEGORIES:
            if tok not in lexicon[cat]:
                continue
            if cat == "positive":
                negated = _is_negated(tokens, i) if negated is None else negated
                if negated:
                    negated_positive += 1
                    continue
            elif cat == "negative" and negate_negatives != "off":
                negated = _is_negated(tokens, i) if negated is None else negated
                if negated:
                    if negate_negatives == "flip":
                        flipped_negative += 1
                    continue
            counts[cat] += 1
    counts["negative"] += negated_positive
    counts["positive"] += flipped_negative

    result: dict[str, float] = {"n_words": float(n)}
    for cat in CATEGORIES:
        result[f"{cat}_rate"] = counts[cat] / n if n else float("nan")
    result["net_tone"] = (
        (counts["positive"] - counts["negative"]) / n if n else float("nan")
    )
    return result
