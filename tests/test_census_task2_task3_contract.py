"""The Task 2 → Task 3 contract. One producer, one consumer, compared in the same file.

⚠ WHY THIS EXISTS. On 2026-08-05 Task 2's output schema broke Task 3's consumer **silently** — no
`accession` column, no bucket equal to `resolved` — so every span fetch would have been skipped and
**the band split would have read `no_topology` for all 2,807 proteins.** A resolvable target
recorded as having no topology is **fabrication, not smoothing**: the category is not lost, it is
invented. Nothing would have crashed. It was found by inspection, in committed code, while executing
something else.

⚠ THE FETCH KEY IS `census_accession` ON THE ROSTER, AT PER-PROTEIN GRAIN. Fetching on
`uniprot_accession` at per-identifier grain would fetch **HLA-B thirty-five times** and weight one
family **83-fold** inside the confidence distribution that is the census's headline use. That is a
grain error producing a plausible, dated, provenanced census — not a naming slip.

⚠ SO THE GRAIN IS ASSERTED, NOT JUST THE COLUMNS. The fixture contains a protein reached by **two**
identifiers; without it, per-identifier and per-protein fetching are indistinguishable and this file
passes under the exact defect it exists to catch (A-017 clause (c)).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import census_verify as cv  # noqa: E402
from core.census_identity import CENSUS_IDENTITY_STATUS, VERIFICATION_BUCKET  # noqa: E402

#: ⚠ THE DISCRIMINATING ROW. Q_MERGED is reached by TWO identifiers — TWO_A names it, TWO_B merged
#: into it. A per-protein fetch sees it once; a per-identifier fetch sees it twice.
FIXTURE = [
    # entry            source     current    status            class          conflict
    ("ONE_HUMAN",     "P00001", "P00001", "active_reviewed", "surface",      "no"),
    ("TWO_A_HUMAN",   "Q_MERGED", "Q_MERGED", "active_reviewed", "surface",   "no"),
    ("TWO_B_HUMAN",   "P00099", "Q_MERGED", "merged",          "surface",      "no"),
    ("DEAD_HUMAN",    "P00003", "P00003", "inactive",        "non_surface",  "no"),
]


def _source(tmp_path: Path) -> Path:
    p = tmp_path / "src.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([cv.SRC_ENTRY, cv.SRC_ACCESSION, cv.CUR_ACCESSION, cv.SRC_STATUS,
                    cv.SRC_CLASS, cv.SRC_CONFLICT])
        w.writerows(FIXTURE)
    return p


def _produce(tmp_path: Path):
    src = _source(tmp_path)
    rows = cv.read_map_rows(src, resolved_on="2026-08-06")
    roster = cv.build_roster(rows, parent_sha256="deadbeef", resolved_on="2026-08-06")
    return rows, roster


# ── (a) the fixture reaches the code ────────────────────────────────────────
def test_the_producer_emits_a_nonzero_number_of_rows(tmp_path):
    """⚠ A consumer that silently skips everything passes every other assertion in this file."""
    rows, roster = _produce(tmp_path)
    assert len(rows) == 4, rows
    assert len(roster) == 3, roster


# ── (b) one property, one test ──────────────────────────────────────────────
def test_the_map_emits_exactly_the_declared_columns(tmp_path):
    """Prove it bites by renaming a column in `MAP_COLUMNS` or in `read_map_rows`."""
    rows, _ = _produce(tmp_path)
    assert tuple(rows[0].keys()) == cv.MAP_COLUMNS, (
        f"accession_map columns drifted from the declared schema.\n"
        f"  declared: {cv.MAP_COLUMNS}\n  emitted : {tuple(rows[0].keys())}")


def test_the_roster_emits_exactly_the_declared_columns_including_the_fetch_key(tmp_path):
    """⚠ `census_accession` is THE fetch key. Prove it bites by renaming it: the assertion names
    the missing column rather than failing somewhere downstream."""
    _, roster = _produce(tmp_path)
    assert tuple(roster[0].keys()) == cv.ROSTER_COLUMNS, (
        f"census_roster columns drifted.\n  declared: {cv.ROSTER_COLUMNS}\n"
        f"  emitted : {tuple(roster[0].keys())}")
    assert "census_accession" in roster[0], (
        "the roster has no `census_accession` — Task 3 has no fetch key and every span fetch would "
        "be skipped, reading `no_topology` for the entire census")


def test_every_verification_bucket_is_in_the_declared_vocabulary(tmp_path):
    """Prove it bites by emitting a bucket value outside `VERIFICATION_BUCKET`."""
    rows, _ = _produce(tmp_path)
    seen = {r["verification_bucket"] for r in rows}
    unknown = seen - set(VERIFICATION_BUCKET)
    assert not unknown, f"bucket value(s) outside the declared vocabulary: {unknown}"


def test_every_identity_status_is_in_the_declared_vocabulary(tmp_path):
    """⚠ F-018's vocabulary. `resolved` is retired; a surviving default lands here loudly."""
    _, roster = _produce(tmp_path)
    unknown = {r["census_identity_status"] for r in roster} - set(CENSUS_IDENTITY_STATUS)
    assert not unknown, f"identity status outside the vocabulary: {unknown}"


# ── (c) the grain — the case where correct and incorrect differ ─────────────
def test_the_roster_is_one_row_per_protein_not_per_identifier(tmp_path):
    """⚠ THE ONE THAT CATCHES THE GRAIN ERROR.

    `Q_MERGED` is reached by TWO identifiers. Per-protein grain yields 3 roster rows from 4 map
    rows; per-identifier grain yields 4. **In production that difference is HLA-B fetched
    thirty-five times and one family weighted 83-fold inside the confidence distribution.**

    Prove it bites by keying the roster on `entry_name` instead of `census_accession`: the count
    becomes 4 and this reds naming the duplicated protein."""
    rows, roster = _produce(tmp_path)
    keys = [r["census_accession"] for r in roster]
    assert len(keys) == len(set(keys)), f"the roster has duplicate census_accession: {keys}"
    assert len(roster) == 3 and len(rows) == 4, (
        f"roster {len(roster)} rows from {len(rows)} map rows — expected 3 from 4. A roster with "
        f"one row per IDENTIFIER fetches a merged protein once per identifier.")


def test_the_fixture_actually_contains_a_two_identifier_protein(tmp_path):
    """⚠ A-017 clause (c), asserted rather than assumed. If this reds, the test above has stopped
    discriminating: with one identifier per protein the two grains are indistinguishable and the
    contract test passes under the defect."""
    _, roster = _produce(tmp_path)
    multi = [r for r in roster if "|" in r["source_identifiers"]]
    assert len(multi) == 1, f"fixture has no two-identifier protein: {[r['source_identifiers'] for r in roster]}"
    assert multi[0]["census_accession"] == "Q_MERGED"
    assert multi[0]["source_identifiers"] == "TWO_A_HUMAN|TWO_B_HUMAN", multi[0]


def test_a_collapse_loses_none_of_its_inputs(tmp_path):
    """⚠ A collapse that loses its inputs is a deletion. Every source identifier survives onto the
    roster row it collapsed into."""
    rows, roster = _produce(tmp_path)
    kept = {n for r in roster for n in r["source_identifiers"].split("|")}
    assert kept == {r["entry_name"] for r in rows}, kept


# ── the consumer side: eligibility gates the fetch, the bucket never does ───
def test_fetch_eligibility_comes_from_status_and_never_from_the_verification_bucket(tmp_path):
    """⚠ `disagrees` is a FACT ABOUT OUR SOURCES, not a statement that a protein is unfetchable.
    If it gated the pipeline a disagreement would silently shrink the census — F-009 arriving
    through a column name. Here TWO_B `disagrees` and its protein is still fetch-eligible."""
    rows, roster = _produce(tmp_path)
    assert any(r["verification_bucket"] == "disagrees" for r in rows), "fixture seeds no disagreement"
    q = next(r for r in roster if r["census_accession"] == "Q_MERGED")
    assert q["fetch_eligible"] == "true", (
        "a protein reached by a disagreeing identifier was excluded from the fetch — the "
        "verification bucket gated the pipeline")
    dead = next(r for r in roster if r["census_accession"] == "P00003")
    assert dead["fetch_eligible"] == "false" and dead["fetch_ineligible_reason"] == "uniprot_inactive", (
        "an ineligible row must carry its REASON — an absence with a cause, never a bare false")


def test_an_unmapped_source_status_raises_rather_than_defaulting(tmp_path):
    """⚠ F-018 in the producer. Prove it bites by adding an `or "active"` fallback."""
    p = tmp_path / "bad.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([cv.SRC_ENTRY, cv.SRC_ACCESSION, cv.CUR_ACCESSION, cv.SRC_STATUS,
                    cv.SRC_CLASS, cv.SRC_CONFLICT])
        w.writerow(["X_HUMAN", "P1", "P1", "resolved", "surface", "no"])
    with pytest.raises(ValueError, match="no mapping into"):
        cv.read_map_rows(p, resolved_on="2026-08-06")


def test_an_absent_id_status_raises_in_categorise_rather_than_defaulting():
    """⚠ THE F-018 TEST THAT WAS MISSING, and its absence was found by the revert proving nothing.

    Restoring `(row.get("id_status") or "resolved")` in `core.census.categorise` left the ENTIRE
    suite green at 503 — because every fixture now carries an explicit status, so the default never
    fired. **A defect the suite cannot observe is a defect the suite does not guard.**

    This passes a row with **no status at all**, which is the only input that distinguishes
    "refuses" from "defaults". Prove it bites by restoring the `or "resolved"`: the raise becomes a
    silent `resolved` and this reds at the `pytest.raises`."""
    from core.census import categorise
    from core.census_identity import UnknownIdentityStatus

    with pytest.raises(UnknownIdentityStatus):
        categorise({"span_aa": 300})                      # ⚠ no id_status key at all
    with pytest.raises(UnknownIdentityStatus):
        categorise({"span_aa": 300, "id_status": ""})     # present but empty
    with pytest.raises(UnknownIdentityStatus):
        categorise({"span_aa": 300, "id_status": "resolved"})   # the retired string


def test_the_absent_status_fixture_reaches_categorise_at_all():
    """⚠ A-017 positive control. A row WITH a valid status must categorise normally, so the raises
    above are about the absent status rather than about `categorise` being broken outright."""
    from core.census import categorise
    assert categorise({"span_aa": 300, "id_status": "active"}) is not None
    assert categorise({"span_aa": None, "id_status": "inactive"}) == "inactive"


def test_a_missing_source_column_raises_naming_it(tmp_path):
    """Prove it bites by dropping `_require_columns`: the run proceeds with empty accessions and
    every bucket becomes `unresolvable` — a confident artifact that is wrong about every row."""
    p = tmp_path / "short.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerow([cv.SRC_ENTRY, cv.SRC_ACCESSION])
    with pytest.raises(cv.SourceSchemaError, match=cv.CUR_ACCESSION):
        cv.read_map_rows(p, resolved_on="2026-08-06")
