"""Unit tests using a tiny made-up lexicon, so no download is needed."""

import math

from earnings_alpha.lexicon import score_text, tokenize
from earnings_alpha.sections import split_sections

LEX = {
    "negative": {"LOSS", "DECLINE"},
    "positive": {"GOOD", "STRONG"},
    "uncertainty": {"MAY", "APPROXIMATELY"},
    "litigious": {"LAWSUIT"},
    "strong_modal": {"WILL"},
    "weak_modal": {"COULD"},
    "constraining": {"REQUIRED"},
}


def test_tokenize_uppercases_and_drops_numbers():
    assert tokenize("Revenue grew 12% to $4.5B") == ["REVENUE", "GREW", "TO", "B"]


def test_rates_are_normalized_by_length():
    r = score_text("good strong loss may nothing here today ok", LEX)
    assert r["n_words"] == 8
    assert r["positive_rate"] == 2 / 8
    assert r["negative_rate"] == 1 / 8
    assert r["uncertainty_rate"] == 1 / 8
    assert r["net_tone"] == (2 - 1) / 8


def test_negated_positive_counts_as_negative():
    r = score_text("results were not good", LEX)
    assert r["positive_rate"] == 0
    assert r["negative_rate"] == 1 / 4


def test_negation_outside_three_word_window_is_ignored():
    r = score_text("not one two three good", LEX)
    assert r["positive_rate"] == 1 / 5


def test_negated_negative_modes():
    text = "we are not seeing any decline"  # 6 words; 'not' is within 3 of 'decline'
    off = score_text(text, LEX)
    drop = score_text(text, LEX, negate_negatives="drop")
    flip = score_text(text, LEX, negate_negatives="flip")
    assert off["negative_rate"] == 1 / 6 and off["positive_rate"] == 0
    assert drop["negative_rate"] == 0 and drop["positive_rate"] == 0
    assert flip["negative_rate"] == 0 and flip["positive_rate"] == 1 / 6
    assert off["net_tone"] < drop["net_tone"] < flip["net_tone"]


def test_negated_negative_outside_window_is_unaffected():
    text = "not one two three decline"
    for mode in ("off", "drop", "flip"):
        r = score_text(text, LEX, negate_negatives=mode)
        assert r["negative_rate"] == 1 / 5


def test_no_later_than_false_hit_is_documented():
    # Known limitation: "no later than" is not a real negation, but the crude
    # window treats it as one and drops the negative word.
    text = "payment no later than decline"
    assert score_text(text, LEX)["negative_rate"] == 1 / 5
    assert score_text(text, LEX, negate_negatives="drop")["negative_rate"] == 0


def test_negation_mode_does_not_touch_other_categories():
    text = "not the lawsuit"
    for mode in ("off", "drop", "flip"):
        assert score_text(text, LEX, negate_negatives=mode)["litigious_rate"] == 1 / 3


def test_invalid_negation_mode_raises():
    import pytest

    with pytest.raises(ValueError):
        score_text("x", LEX, negate_negatives="sideways")


def test_empty_text_gives_nan_rates():
    r = score_text("", LEX)
    assert r["n_words"] == 0
    assert math.isnan(r["net_tone"])


def test_split_sections_finds_qa():
    body = "prepared remarks " * 100
    text = body + "We will now begin the question-and-answer session. " + "q " * 50
    prepared, qa = split_sections(text)
    assert qa is not None and qa.lower().startswith("question-and-answer")
    assert "prepared remarks" in prepared


def test_split_sections_no_marker():
    prepared, qa = split_sections("just a monologue " * 50)
    assert qa is None and prepared
