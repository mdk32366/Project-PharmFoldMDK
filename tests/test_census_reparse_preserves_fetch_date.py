"""A re-parse changes the parse. It does NOT change when the data was fetched.

⚠ **AMENDMENT A1.2, AND IT IS THE BINDING CONSTRAINT.** The census was fetched 2026-08-06 at a
specific UniProt release. **Only the parse changed.** A re-parse that overwrote `fetched_on` would
manufacture provenance for data that did not move — turning a one-day pull into a two-day pull as an
artifact of housekeeping, **which is the date rule tripped by its own maintenance.**

⚠ **A-017 clause (c) is the whole design of this file.** The date assertion only discriminates on a
row **whose span actually changes** — on an unchanged row a restamping implementation and a
preserving one are indistinguishable, and the test would pass under the defect it exists to catch.
So the fixture carries a `Lumenal` protein that gains 681 aa, and a separate test asserts that it
really does gain it.
"""

from __future__ import annotations

import csv
import json

import pytest

from scripts.census_reparse import V1_COLUMN, reparse_row

FETCHED_ON = "2026-08-06"
RELEASE = "2026-06-10"


def _v1_row(acc, *, span="", reason="no sliceable ECD span in the fetched entry"):
    """A row exactly as `spans_*.csv` holds it."""
    return {"census_accession": acc, "census_class": "surface", "census_identity_status": "active",
            "source_identifiers": acc, "span_aa": span, "no_topology_reason": reason,
            "fetch_failed": "false", "fetch_error": "", "fetched_on": FETCHED_ON,
            "uniprot_release": RELEASE}


def _lumenal_entry():
    """⚠ Gains a span under V2 and had none under V1 — the discriminating shape."""
    return {"features": [
        {"type": "Topological domain", "description": "Lumenal",
         "location": {"start": {"value": 24, "modifier": "EXACT"},
                      "end": {"value": 704, "modifier": "EXACT"}}}],
        "sequence": {"length": 904}}


@pytest.fixture()
def cached(tmp_path, monkeypatch):
    """Point the re-parser's cache at a temp dir holding one entry. ⚠ No network, by construction."""
    import scripts.census_reparse as m
    d = tmp_path / "spancache"
    d.mkdir()
    (d / "TESTACC.json").write_text(json.dumps(_lumenal_entry()), encoding="utf-8")
    monkeypatch.setattr(m, "CACHE", d)
    return d


# ── (a) the fixture reaches the code ────────────────────────────────────────
def test_the_fixture_row_actually_gains_a_span(cached):
    """⚠ A-017 clause (c), asserted rather than assumed. If this reds, the date test below has
    stopped discriminating: on a row whose span does not change, a restamping implementation and a
    preserving one produce identical output."""
    out = reparse_row(_v1_row("TESTACC"), commit="deadbeef")
    assert out[V1_COLUMN] == "", "the fixture already had a V1 span — it cannot show a gain"
    assert out["span_aa"] == 681, out
    assert out["span_rule"] == "vocabulary"


# ── (b) one property, one test ──────────────────────────────────────────────
def test_fetched_on_is_byte_identical_across_a_reparse_that_changes_the_span(cached):
    """⚠⚠ THE ASSERTION THE AMENDMENT NAMES. Prove it bites by restamping — replace the carried
    `fetched_on` with `datetime.date.today().isoformat()` in `reparse_row`: this reds HERE, at the
    date, and not at a row count, which would move under either implementation."""
    before = _v1_row("TESTACC")
    after = reparse_row(before, commit="deadbeef")
    assert after["span_aa"] == 681, "the fixture stopped discriminating — see the test above"
    assert after["fetched_on"] == before["fetched_on"] == FETCHED_ON, (
        f"fetched_on moved {before['fetched_on']!r} → {after['fetched_on']!r} across a re-parse. "
        f"The data did not move; only the parse did. A restamped date manufactures provenance.")


def test_uniprot_release_is_preserved_too(cached):
    before = _v1_row("TESTACC")
    after = reparse_row(before, commit="deadbeef")
    assert after["uniprot_release"] == before["uniprot_release"] == RELEASE


def test_parsed_under_names_the_definition_and_the_commit(cached):
    """⚠ A span whose definition is unknown is a span whose meaning is unknown (D-081)."""
    after = reparse_row(_v1_row("TESTACC"), commit="deadbeef")
    assert after["parsed_under"] == "v2-ruled-vocabulary-2026-08-07@deadbeef"


def test_the_v1_span_is_carried_beside_the_v2_span_rather_than_replaced(cached):
    """⚠ D-081: two definitions, both named. A file that kept only the new number would make the
    comparison impossible and the correction uncheckable."""
    after = reparse_row(_v1_row("TESTACC", span="123"), commit="x")
    assert after[V1_COLUMN] == "123"


# ── the never-fetched and the cache miss ────────────────────────────────────
def test_a_never_fetched_row_takes_no_v2_category_and_keeps_its_reason(cached):
    """⚠ It was never asked. A re-parse cannot make a claim about a protein nobody looked at."""
    row = _v1_row("NEVER", reason="not fetched: uniprot_inactive")
    row["fetched_on"] = ""
    out = reparse_row(row, commit="x")
    assert out["span_aa"] == "" and out["span_category"] == ""
    assert out["no_span_reason"] == "not fetched: uniprot_inactive"
    assert out["parsed_under"] == "", "a never-fetched row was stamped with a parse definition"


def test_a_missing_cache_entry_is_named_and_not_refetched(cached):
    """⚠ A partial re-fetch would put two fetch dates in one file. Prove it bites by adding a
    network fallback: the reason disappears and this reds."""
    out = reparse_row(_v1_row("NOTINCACHE"), commit="x")
    assert out["span_category"] == "absent_with_reason"
    assert "NOT re-fetched" in out["no_span_reason"]
    assert out["fetched_on"] == FETCHED_ON, "a cache miss disturbed the fetch date"
