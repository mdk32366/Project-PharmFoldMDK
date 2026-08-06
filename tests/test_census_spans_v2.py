"""Census Task 3 — the span pull's provenance rules, and the dormancy of the superseded map script.

⚠ THE DATE RULE IS THE POINT. A rate-limited pull of 2,807 proteins may not finish in one sitting.
One "run date" stamped across records fetched on two days is a plausible, dated, provenanced, wrong
artifact. Every record carries its own `fetched_on`; the header reports FIRST and LAST; a single
`as_of_date` is emitted only when they agree.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import census_spans_v2 as cs  # noqa: E402


def _entry(acc, *, cls="surface", status="active", eligible="true", reason="", ids=None):
    return {"census_accession": acc, "census_class": cls, "census_identity_status": status,
            "source_identifiers": ids or acc, "fetch_eligible": eligible,
            "fetch_ineligible_reason": reason}


def _roster(tmp_path, entries):
    p = tmp_path / "roster.csv"
    cols = ["census_accession", "census_class", "census_identity_status", "source_identifiers",
            "fetch_eligible", "fetch_ineligible_reason"]
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(entries)
    return p


# ── the date rule ───────────────────────────────────────────────────────────
def test_a_single_day_pull_emits_one_as_of_date():
    rows = [cs.span_row(_entry("P1"), {}, None, fetched_on="2026-08-06"),
            cs.span_row(_entry("P2"), {}, None, fetched_on="2026-08-06")]
    prov = cs.provenance(rows)
    assert prov["as_of_date"] == "2026-08-06"
    assert prov["spans_multiple_days"] is False


def test_a_two_day_pull_reports_both_and_emits_no_single_as_of_date():
    """⚠ THE DISCRIMINATING CASE. Prove it bites by collapsing to `dates[0]` or `max(dates)`:
    `as_of_date` becomes a date that is true of some records and false of others, and this reds."""
    rows = [cs.span_row(_entry("P1"), {}, None, fetched_on="2026-08-06"),
            cs.span_row(_entry("P2"), {}, None, fetched_on="2026-08-07")]
    prov = cs.provenance(rows)
    assert prov["first_fetched_on"] == "2026-08-06"
    assert prov["last_fetched_on"] == "2026-08-07"
    assert prov["spans_multiple_days"] is True
    assert prov["as_of_date"] == "", (
        f"a single as_of_date {prov['as_of_date']!r} was emitted for a pull spanning two days — "
        "true of some records and false of others")


def test_the_two_day_fixture_actually_contains_two_dates():
    """⚠ A-017. With one date the test above passes under a collapsing implementation — the world
    would be too small to contain the bug, which is how three fixtures failed on 2026-08-06."""
    rows = [cs.span_row(_entry("P1"), {}, None, fetched_on="2026-08-06"),
            cs.span_row(_entry("P2"), {}, None, fetched_on="2026-08-07")]
    assert len({r["fetched_on"] for r in rows}) == 2


# ── absence is always a category ────────────────────────────────────────────
def test_a_fetch_failure_is_not_no_topology_and_not_an_identity_failure():
    """⚠ `no_topology` REQUIRES A SUCCESSFUL FETCH. Prove it bites by writing span_aa=0 or by
    setting no_topology_reason on the error path."""
    r = cs.span_row(_entry("P1"), None, "TimeoutError: took too long", fetched_on="2026-08-06")
    assert r["fetch_failed"] == "true" and r["fetch_error"]
    assert r["span_aa"] == "", "a failed fetch produced a span"
    assert r["no_topology_reason"] == "", (
        "a failed fetch was recorded as no_topology — the identity is intact and the request is "
        "what failed; that would be a claim about the protein made without looking")


def test_no_topology_is_a_reason_never_a_zero():
    r = cs.span_row(_entry("P1"), {}, None, fetched_on="2026-08-06")
    assert r["span_aa"] == "" and r["no_topology_reason"], r
    assert r["span_aa"] != 0 and r["span_aa"] != "0"


def test_an_ineligible_row_is_not_fetched_and_says_why():
    rows = cs.pull([_entry("P1", status="inactive", eligible="false", reason="uniprot_inactive")],
                   cache=None, sleep_s=0, today="2026-08-06")
    assert rows[0]["fetched_on"] == "", "an ineligible row was fetched"
    assert "uniprot_inactive" in rows[0]["no_topology_reason"]


# ── the band split: where the never-fetched land, and the declared denominator ──
def _srow(acc, status, *, reason="", fetched="", span="", failed="false"):
    return {"census_accession": acc, "census_class": "surface", "census_identity_status": status,
            "source_identifiers": acc, "span_aa": span, "no_topology_reason": reason,
            "fetch_failed": failed, "fetch_error": "", "fetched_on": fetched, "uniprot_release": ""}


def test_a_never_fetched_row_is_not_no_topology_and_names_its_reason():
    """⚠ AN UNFETCHED PROTEIN IS NOT A PROTEIN WITH NO TOPOLOGY. It was never asked.

    In production this is exactly **7 rows of 2,807** — the inactive surface proteins — and at that
    size an absorption into `no_topology` is *harder* to notice, not easier. The band names the
    reason so it can never be read as a topology claim.

    Prove it bites by keying never-fetched rows on `census_identity_status` alone, or by letting
    them fall through to `categorise`: the band becomes `inactive` or `no_topology` and this reds."""
    split = band_of([_srow("A6NKC4", "inactive", reason="not fetched: uniprot_inactive")])
    assert "no_topology" not in split, (
        f"a never-fetched protein was counted as having no topology: {split}")
    assert "fetch_ineligible:uniprot_inactive" in split, split


def test_the_band_split_declares_its_denominator_and_does_not_absorb_the_unfetched():
    """⚠ Either *N fetched with the ineligible named beside it* or *N total with
    fetch_ineligible as its own band* — **never N total with them silently absorbed.**
    This is the count where it is easiest to lose rows into a plausible total.

    Prove it bites by dropping `denominator_fetch_ineligible`, or by summing the ineligible into
    `denominator_fetched`: the two denominators stop reconciling and this reds."""
    import census_spans_v2 as m
    rows = [_srow("A", "active", fetched="2026-08-06", span=300),
            _srow("B", "active", fetched="2026-08-06", reason="no sliceable ECD span"),
            _srow("C", "inactive", reason="not fetched: uniprot_inactive")]
    s = m.band_split(rows)
    assert s["denominator_total_rows"] == 3
    assert s["denominator_fetched"] == 2
    assert s["denominator_fetch_ineligible"] == 1
    assert s["denominator_fetched"] + s["denominator_fetch_ineligible"] == s["denominator_total_rows"], s
    assert sum(s["bands"].values()) == s["denominator_total_rows"], (
        "the bands do not sum to the declared total — rows were lost or double-counted")


def test_the_band_split_names_the_ceiling_recipe_as_a_triple():
    """⚠ D-077 dec 3: the ceiling is a triple, never a bare integer. A band split read under a
    recipe it was not measured under is a different measurement wearing the same name."""
    import census_spans_v2 as m
    s = m.band_split([_srow("A", "active", fetched="2026-08-06", span=300)])
    for token in ("dtype=", "chunk_size=", "known_good="):
        assert token in s["ceiling_recipe"], (token, s["ceiling_recipe"])


def test_the_denominator_fixture_actually_contains_an_unfetched_row():
    """⚠ A-017 clause (c). With every row fetched, the two tests above pass under an
    implementation that absorbs the ineligible — the fixture's world would be too small to hold
    the bug, which is how three fixtures failed on 2026-08-06."""
    rows = [_srow("A", "active", fetched="2026-08-06", span=300),
            _srow("C", "inactive", reason="not fetched: uniprot_inactive")]
    assert sum(1 for r in rows if not r["fetched_on"]) == 1


def band_of(rows):
    import census_spans_v2 as m
    return m.band_split(rows)["bands"]


# ── the unclassified are not pulled ─────────────────────────────────────────
def test_the_unclassified_cannot_be_pulled_even_by_asking(tmp_path):
    """⚠ F-016. Prove it bites by adding `unclassified` to the --class choices."""
    p = _roster(tmp_path, [_entry("P1", cls="unclassified")])
    with pytest.raises(cs.UnclassifiedPullRefused):
        cs.read_roster(p, "unclassified")


def test_an_empty_class_selection_refuses_rather_than_writing_an_empty_file(tmp_path):
    """⚠ A pull that matches nothing must not emit a confident empty artifact."""
    p = _roster(tmp_path, [_entry("P1", cls="surface")])
    with pytest.raises(ValueError, match="no rows of class"):
        cs.read_roster(p, "non_surface")


def test_the_roster_fixture_reaches_the_reader_at_all(tmp_path):
    """⚠ A-017 positive control for the two refusals above."""
    p = _roster(tmp_path, [_entry("P1", cls="surface"), _entry("P2", cls="non_surface")])
    assert len(cs.read_roster(p, "surface")) == 1


# ── §4: the superseded map script's dormancy, made structural ───────────────
CENSUS_MODULES = ("scripts/census_verify.py", "scripts/census_spans_v2.py", "core/census.py",
                  "core/census_identity.py")


def test_no_census_path_imports_the_superseded_accession_map_script():
    """⚠ `scripts/accession_map.py` is the 2026-08-04 DERIVATION script, superseded by
    `census_verify.py`'s verification. The census order ruled that re-deriving the mapping "would
    create a second accession source with nothing comparing them" — **that script is that second
    source**, and it still holds the retired `RESOLVED = "resolved"` vocabulary.

    Deleting it is an owner call. Making its dormancy STRUCTURAL is not: no census path imports it,
    and this asserts that rather than hoping.

    Prove it bites by adding `import accession_map` to any module above."""
    import re
    for rel in CENSUS_MODULES:
        src = (REPO / rel).read_text(encoding="utf-8")
        assert not re.search(r"^\s*(from|import)\s+.*\baccession_map\b", src, re.M), (
            f"{rel} imports the superseded scripts/accession_map.py — that is the second accession "
            f"source the census order refused, re-entering the census path")


def test_the_import_scan_actually_reads_nonempty_modules():
    """⚠ A-017 clause (a). A scan over missing or empty files passes trivially."""
    for rel in CENSUS_MODULES:
        assert (REPO / rel).exists(), rel
        assert len((REPO / rel).read_text(encoding="utf-8")) > 500, rel
