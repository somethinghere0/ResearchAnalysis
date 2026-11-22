"""Split a transcript into prepared remarks and Q&A.

This is a HEURISTIC written before looking at the real data. Transcript
formats differ by source, so verify it against the actual dataset (and fix
the markers) before trusting any prepared-vs-Q&A feature.
"""

from __future__ import annotations

import re

# Matches the typical operator hand-off, e.g. "Question-and-Answer Session",
# "Q&A", "we will now begin the question and answer session".
_QA_MARKER = re.compile(
    r"(question[\s\-–]*(and|&)[\s\-–]*answer(s)?(\s+session)?"
    r"|\bq\s*&\s*a\b"
    r"|open (the|it up|up the) (floor|line|lines) (for|to) questions)",
    re.IGNORECASE,
)


def split_sections(transcript: str) -> tuple[str, str | None]:
    """Return (prepared_remarks, qa). qa is None if no marker was found.

    Uses the FIRST marker after the first 5% of the text, so a mention of
    "Q&A" in the opening safe-harbor statement doesn't split too early.
    """
    text = transcript or ""
    start = int(len(text) * 0.05)
    match = _QA_MARKER.search(text, pos=start)
    if match is None:
        return text, None
    return text[: match.start()], text[match.start() :]
