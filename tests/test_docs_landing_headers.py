"""Dated docs/ artefacts carry a landing header, and the check normalises before matching.

⚠ WHY NORMALISATION IS THE POINT OF THIS FILE, NOT A DETAIL.  The first version of this check
was a fixed-string grep for `THE LOG GOVERNS`.  It was RUN, and it returned 11 where 12 was
correct: `D-079-census-ingest-tranches-and-recipe-v2.md` wraps the phrase across a line break
as `THE LOG\n> GOVERNS`.  **It under-reported in the direction that looks safe** -- a document
that DID carry a header was counted as one that did not, so the error surfaced as extra work
rather than as a false pass.  The next such wrap will not be so kind.

⚠ THE DATE FLOOR IS 2026-08-05 AND IT IS NOT ARBITRARY.  The landing-header convention was
created by `docs/RULING-2026-08-05-D-079-denominators-in-the-log.md` §3 ("Every staged
2026-08-05 document gains a landing header in the same commit").  It was never retroactive.
Without the floor this check matches 44 files back to 2026-07-26 and fails on 23 of them --
asserting a convention over documents that predate it by six weeks.

⚠ A-017 (the fixture must reach the code under test) IS APPLIED THREE WAYS HERE:
  (a) discovery is asserted NON-ZERO -- a check that silently matches nothing passes everything;
  (b) discovery, normalisation and header-presence get SEPARATE tests -- a compound test proves
      only its first failing assertion;
  (c) the fixture contains a case where correct and incorrect DIFFER: the wrapped header.  The
      no-header case reds under both the correct and the broken implementation and therefore
      proves nothing on its own.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parent.parent / "docs"

# The convention's own name for itself. Matched AFTER normalisation, never before.
LANDING_MARKER = "THE LOG GOVERNS"

# Dated-artefact prefixes. `CLOSEOUT-*` and `PREWORK-*` are DELIBERATELY ABSENT rather than
# filtered out later: they are session records, not landing artefacts, and they carry a
# session-record header instead. Widening this pattern to catch them would assert the wrong
# convention over them (Planner ruling, PR #129).
ARTEFACT_PREFIX = re.compile(
    r"^(RULING|RULINGS|ORDERS|CORRECTION|AMENDMENT|SPEC|AUTHORISATION|META-ORDER)"
)
DATE_IN_NAME = re.compile(r"2026-(\d{2})-(\d{2})")

# Created by RULING-2026-08-05-D-079-denominators-in-the-log.md §3; not retroactive.
CONVENTION_FLOOR = "2026-08-05"

HEADER_WINDOW_LINES = 12


def normalise(text: str) -> str:
    """Collapse blockquote markers and whitespace runs so a wrapped phrase matches.

    ⚠ Order matters: the `> ` is stripped PER LINE first, then all whitespace runs collapse.
    Doing it the other way round leaves `THE LOG > GOVERNS`, which still does not match and
    would reproduce the original defect while looking normalised.
    """
    unquoted = [re.sub(r"^\s*>\s?", "", line) for line in text.splitlines()]
    return re.sub(r"\s+", " ", " ".join(unquoted)).strip()


def discovered_documents() -> list[Path]:
    """Dated artefacts at or after the convention's floor."""
    out: list[Path] = []
    for path in sorted(DOCS.glob("*.md")):
        if not ARTEFACT_PREFIX.match(path.name):
            continue
        match = DATE_IN_NAME.search(path.name)
        if match is None:
            continue
        if f"2026-{match.group(1)}-{match.group(2)}" < CONVENTION_FLOOR:
            continue
        out.append(path)
    return out


def header_window(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()[:HEADER_WINDOW_LINES]
    return normalise("\n".join(lines))


# ── (a) discovery must find something ────────────────────────────────────────
def test_discovery_matches_a_nonzero_number_of_files():
    """⚠ A check that matches nothing passes everything. Prove it bites by tightening the
    prefix to a string no file starts with: discovery empties and this reds."""
    found = discovered_documents()
    assert found, (
        "discovery matched ZERO documents -- this check would then pass vacuously over an "
        f"empty set. Looked in {DOCS} for {ARTEFACT_PREFIX.pattern} dated >= {CONVENTION_FLOOR}"
    )


def test_the_floor_excludes_documents_that_predate_the_convention():
    """The floor is load-bearing, not cosmetic: without it this check asserts a 2026-08-05
    convention over July orders. Prove it bites by removing the floor comparison."""
    all_dated = [p for p in sorted(DOCS.glob("*.md"))
                 if ARTEFACT_PREFIX.match(p.name) and DATE_IN_NAME.search(p.name)]
    discovered = discovered_documents()
    excluded = set(all_dated) - set(discovered)
    assert excluded, (
        "the floor excluded nothing, so it is untested here -- either the pre-convention "
        "documents have been removed, or the floor stopped being applied")
    for path in excluded:
        match = DATE_IN_NAME.search(path.name)
        assert f"2026-{match.group(1)}-{match.group(2)}" < CONVENTION_FLOOR, path.name


# ── (b) one property per test: normalisation, on fixtures, in isolation ──────
ONE_LINE = "# T\n\n> **Where this file and the log differ, THE LOG GOVERNS.** Provenance.\n"
WRAPPED = "# T\n\n> **Where this file and the log differ, THE LOG\n> GOVERNS.** Provenance.\n"
ABSENT = "# T\n\n> **Provenance only.** This document names no governing artefact.\n"


def test_normalisation_joins_a_header_wrapped_across_a_line_break():
    """⚠ THE DISCRIMINATING CASE, and the revert target.

    Under a broken normalisation (identity, or one that collapses whitespace WITHOUT first
    stripping the `> `), the wrapped fixture yields `THE LOG > GOVERNS` or `THE LOG\\n> GOVERNS`
    -- neither matches -- and this assertion reds. The absent fixture reds under BOTH
    implementations, so it cannot prove normalisation works; this one can."""
    assert LANDING_MARKER in normalise(WRAPPED), (
        "a header wrapped across a line break was not matched -- this is the exact defect that "
        "made a fixed-string grep report 11 where 12 was correct")


def test_normalisation_leaves_a_single_line_header_matched():
    assert LANDING_MARKER in normalise(ONE_LINE)


def test_normalisation_does_not_invent_a_header_where_there_is_none():
    """⚠ Reds under a correct AND a broken implementation, so it proves nothing about
    normalisation. It is here to stop the opposite failure: a normaliser so aggressive it
    matches anything."""
    assert LANDING_MARKER not in normalise(ABSENT)


# ── ⚠ THE KNOWN LIMIT, ASSERTED RATHER THAN LEFT IMPLICIT (D-074, second clause) ──
# A document that QUOTES the marker in its first 12 lines passes without carrying a header. This
# check is a presence test; it cannot distinguish USE from MENTION.
QUOTED_ONLY = (
    "# SPEC — 2026-08-06 — What a landing header must say\n\n"
    "## The convention\n\n"
    "Every dated artefact carries, verbatim:\n\n"
    "```\n"
    "> **Where this file and the log differ, THE LOG GOVERNS.**\n"
    "```\n\n"
    "This document does NOT carry one itself.\n"
)


def test_the_check_cannot_tell_use_from_mention_and_says_so():
    """⚠ A KNOWN LIMIT, pinned so it is explicit rather than discovered.

    `QUOTED_ONLY` carries NO landing header — it only quotes the marker as an example — and this
    check passes it anyway. **That is the exact defect that produced F-024's first two instances:**
    #123 and #129 both matched the header template quoted inside
    `RULING-2026-08-05-D-079-denominators-in-the-log.md` §3, and that file went unheaded for a day.

    The 12-line window makes it rare — a document usually mentions the marker well below its own
    header — but rare is not never, and this file is itself in the discovery set, as is
    `SPEC-2026-08-06-landing-header-matcher.md`, whose whole subject is the marker string.

    ⚠ This test asserts the WRONG-BUT-CURRENT behaviour on purpose. If a future change makes the
    check position-aware or quote-aware, this reds — and that red is the fix landing, not a
    regression. Update it deliberately; do not delete it to make the suite green."""
    window = normalise("\n".join(QUOTED_ONLY.splitlines()[:HEADER_WINDOW_LINES]))
    assert LANDING_MARKER in window, "fixture precondition: the marker must appear as quoted content"
    assert "Where this file and the log differ" in window, (
        "the marker appears only inside a fenced example, not as a header")


# ── (b) header presence, as its own test, over the real tree ────────────────
def test_every_discovered_document_carries_a_landing_header():
    missing = [p.name for p in discovered_documents() if LANDING_MARKER not in header_window(p)]
    assert not missing, (
        f"{len(missing)} dated artefact(s) at or after {CONVENTION_FLOOR} carry no landing "
        f"header in their first {HEADER_WINDOW_LINES} lines: {missing}")


def test_the_excluded_session_records_are_excluded_by_name_not_by_accident():
    """`CLOSEOUT-*` / `PREWORK-*` are session records carrying a different header. If either
    ever starts matching, this check would begin asserting the wrong convention over them."""
    names = [p.name for p in discovered_documents()]
    assert not [n for n in names if n.startswith(("CLOSEOUT", "PREWORK"))], names


# ── the known gap, ASSERTED rather than described ───────────────────────────
D079_STAGED = DOCS / "D-079-census-ingest-tranches-and-recipe-v2.md"


@pytest.mark.skipif(not D079_STAGED.exists(), reason="staged D-079 entry not present")
def test_the_d079_staged_entry_is_a_known_and_uncovered_gap():
    """⚠ AN ASSERTED KNOWN GAP, NOT A COMMENT -- because a comment drifts silently and an
    assertion does not.

    `D-079-census-ingest-tranches-and-recipe-v2.md` is the document whose wrapped header caused
    the original miscount, and **this check cannot see it**: it matches neither the artefact
    prefix nor the date-in-filename requirement. It is nonetheless compliant. Three assertions
    pin all three of those facts, so that if ANY of them changes -- the file is renamed into
    coverage, the date convention changes, or the header is lost -- this reds and the gap is
    re-examined deliberately instead of being discovered by its absence."""
    assert ARTEFACT_PREFIX.match(D079_STAGED.name) is None, (
        "the staged D-079 entry now matches the artefact prefix -- it is no longer a gap, so "
        "delete this test and let the main check cover it")
    assert DATE_IN_NAME.search(D079_STAGED.name) is None, (
        "the staged D-079 entry now carries a date in its filename -- re-derive whether the "
        "main check reaches it")
    assert LANDING_MARKER in normalise(D079_STAGED.read_text(encoding="utf-8")), (
        "the staged D-079 entry lost its landing header, and NO automated check covers it -- "
        "that is precisely why this gap is asserted rather than described")
