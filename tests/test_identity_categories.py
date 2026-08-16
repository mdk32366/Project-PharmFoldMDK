"""F-036 — a row with no span must never carry an empty `span_category`.

⚠ The defect was not that the re-parse withheld a *span* judgement on a never-fetched row — that was
correct, no such judgement exists. **It was that "no judgement" was encoded as the SAME EMPTY STRING
a row WITH a span carries**, so `span_category == ""` meant both *"has a span"* and *"never looked
at"*. One band meaning two things, which is F-025's shape in the field meant to have fixed it.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.census_reparse import (  # noqa: E402
    IDENTITY_DELETED, IDENTITY_DEMERGED, IDENTITY_UNRESOLVED, _identity_category,
)

CENSUS = REPO / "data" / "census"


def test_an_identity_category_is_never_blank():
    """⚠⚠ THE INVARIANT. Blank is the value that caused the defect; it must be unreachable."""
    for acc in ("A6NKC4", "P33765", "P04626", "", "NOT_AN_ACCESSION"):
        assert _identity_category(acc).strip(), f"{acc!r} produced a blank category"


def test_never_looked_and_looked_and_gone_are_different_categories():
    """⚠ Absence of evidence vs evidence of absence — they lead to opposite actions: one is
    resolvable by fetching, the other is permanent."""
    assert _identity_category("A6NKC4") == IDENTITY_DELETED
    assert _identity_category("P33765") == IDENTITY_DEMERGED
    # ⚠ An accession with no resolution row is UNRESOLVED, never DELETED. Guessing "deleted" for
    # something nobody asked about would assert a withdrawal that never happened.
    assert _identity_category("P04626") == IDENTITY_UNRESOLVED
    assert len({IDENTITY_DELETED, IDENTITY_DEMERGED, IDENTITY_UNRESOLVED}) == 3


def test_a_missing_resolution_file_is_a_category_not_a_crash_and_not_a_blank(monkeypatch):
    """⚠ The file is an artifact and may be absent in a fresh clone. Absent must degrade to
    `identity_unresolved` — a stated 'nobody has looked' — never to a blank or an exception."""
    import scripts.census_reparse as cr
    monkeypatch.setattr(cr, "CENSUS", REPO / "data" / "census" / "__does_not_exist__")
    assert cr._identity_category("A6NKC4") == IDENTITY_UNRESOLVED


def test_the_resolution_artifact_never_claims_a_sequence():
    """⚠⚠ An inactive UniProt entry carries NO sequence — measured, all 26. A resolution converts
    'unknown' into a stated reason; it does NOT produce a foldable row, and any future edit
    implying otherwise would put an unfoldable accession back in the manifest's path."""
    path = CENSUS / "census_identity_resolution.csv"
    if not path.is_file():
        pytest.skip("resolution artifact absent")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows, "the artifact is empty — that is not a resolution"
    assert all(r["carries_sequence"] == "false" for r in rows)
    # ⚠ `resolvable` is a SENTENCE, not a bool: DELETED and DEMERGED are resolvable in different
    # senses and a boolean would flatten them.
    assert all(r["resolvable"].strip() for r in rows)
    for r in rows:
        if r["resolution"] == "DEMERGED":
            assert int(r["target_count"]) >= 1, "a demerge with no target is not a demerge"
        elif r["resolution"] == "DELETED":
            assert r["targets"] == "", "a deletion with a target is a merge, not a deletion"


def test_the_span_files_were_not_restamped_by_the_resolution_run():
    """⚠⚠ TWO FACTS, NEVER ONE DATE. The spans were fetched 2026-08-06; the resolution ran later.
    Rewriting `fetched_on` would manufacture provenance for data that did not move."""
    for f in ("spans_surface.v2.csv", "spans_annex.v2.csv"):
        path = CENSUS / f
        if not path.is_file():
            pytest.skip(f"{f} absent")
        dates = {r["fetched_on"] for r in csv.DictReader(path.open(encoding="utf-8"))
                 if r["fetched_on"]}
        assert dates == {"2026-08-06"}, f"{f} carries fetch dates {dates} — restamped?"
