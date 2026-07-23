"""D-040 + D-029 — ADC reference tests, the surface written before the code (project rule).

Pure and hermetic: real committed data for the published evidence scores (they ARE the data), and
fixtures for the curated mapping (whose roster is a reserved hand-review). No network anywhere — the
live openFDA query is the scheduled advisory workflow's, never the suite's.
"""

from __future__ import annotations

import pytest

from core.adc_reference import (
    ADC_MAPPING,
    SCORE_NOT_PUBLISHED,
    CurationError,
    cohort_accessions,
    group_b,
    group_b_accessions,
    group_b_folded_count,
    group_c,
    load_evidence_scores,
    load_mapping,
    reconcile_approvals,
    with_in_cohort,
)

# A real in-cohort accession (NECTIN4, id 1) and a deliberately out-of-cohort one for Group C.
IN_COHORT = "Q96NY8"
OUT_OF_COHORT = "P99999"


def _write(path, header, rows):
    lines = [header] + [",".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


MAP_HEADER = "drug,application_number,antigen,uniprot_accession,source_citation,marketing_status,development_stage"


# ── evidence score: 17 published, 65 null-with-reason, no imputation (D-040 dec. 2) ──

def test_evidence_scores_17_published_65_null_with_reason():
    out = load_evidence_scores()                       # real committed data
    scores = out["scores"]
    assert len(scores) == 82                           # every cohort target represented
    scored = [s for s in scores if s["evidence_score"] is not None]
    null = [s for s in scores if s["evidence_score"] is None]
    assert len(scored) == 17 and len(null) == 65       # D-040: exactly 17 from the text
    assert all(1 <= s["evidence_score"] <= 5 for s in scored)
    # the 65 carry a REASON and never an imputed number
    assert all(s["null_reason"] == SCORE_NOT_PUBLISHED for s in null)
    assert out["unresolved"] == []                     # all 17 published symbols join to the cohort


def test_evidence_score_join_miss_is_surfaced_not_dropped(tmp_path):
    # a published symbol not in the cohort must appear in `unresolved`, never silently vanish
    scores = _write(tmp_path / "s.csv", "symbol,evidence_score,source_citation",
                    [["NOTREAL", "5", "fixture"]])
    out = load_evidence_scores(scores_path=scores)
    assert "NOTREAL" in out["unresolved"]
    assert all(s["symbol"] != "NOTREAL" for s in out["scores"])


def test_no_imputation_anywhere():
    # belt-and-braces: no cohort target without a published score ever gets a number
    for s in load_evidence_scores()["scores"]:
        if s["null_reason"] == SCORE_NOT_PUBLISHED:
            assert s["evidence_score"] is None


# ── the curated mapping: citations + computed in_cohort_82 (D-029 + D-040) ──

def test_uncited_mapping_row_is_rejected(tmp_path):
    path = _write(tmp_path / "m.csv", MAP_HEADER,
                  [["drugX", "", "ANTG", IN_COHORT, "", "", "clinical"]])   # empty source_citation
    with pytest.raises(CurationError):
        load_mapping(path)


def test_typed_in_cohort_82_column_is_rejected(tmp_path):
    # in_cohort_82 is COMPUTED (D-040); a curated file that TYPES it is a slip that could move a
    # target between Group B and Group C — load_mapping must refuse it.
    header = MAP_HEADER + ",in_cohort_82"
    path = _write(tmp_path / "m.csv", header,
                  [["drugX", "", "ANTG", IN_COHORT, "cite", "", "clinical", "true"]])
    with pytest.raises(CurationError):
        load_mapping(path)


def test_the_committed_scaffold_loads_empty_and_valid():
    # the real file is the schema + discipline with no roster yet — loads to [] without error
    assert load_mapping(ADC_MAPPING) == []


# ── Group B / Group C by pure function; in_cohort_82 computed by join (D-040 dec. 1/3) ──

def _mapping(tmp_path):
    return _write(tmp_path / "m.csv", MAP_HEADER, [
        ["enfortumab vedotin", "761137", "NECTIN4", IN_COHORT, "Padcev label", "approved", "approved"],
        ["fixture preclinical", "", "ANTG", IN_COHORT, "cite", "", "preclinical"],
        ["out-of-cohort ADC", "999999", "OTHER", OUT_OF_COHORT, "cite", "approved", "approved"],
    ])


def test_in_cohort_82_is_computed_by_join(tmp_path):
    rows = load_mapping(_mapping(tmp_path))
    enriched = {r["uniprot_accession"]: r["in_cohort_82"] for r in with_in_cohort(rows, cohort_accessions())}
    assert enriched[IN_COHORT] is True                 # computed against the real cohort
    assert enriched[OUT_OF_COHORT] is False


def test_group_b_is_in_cohort_group_c_is_out(tmp_path):
    rows = load_mapping(_mapping(tmp_path))
    accs = cohort_accessions()
    b = group_b_accessions(rows, accs)
    c = {r["uniprot_accession"] for r in group_c(rows, accs)}
    assert IN_COHORT in b and OUT_OF_COHORT not in b   # Group B ⊆ in-cohort
    assert OUT_OF_COHORT in c and IN_COHORT not in c   # Group C ⊆ out-of-cohort
    assert b.isdisjoint(c)                             # a target is never in both


def test_group_b_count_is_pinned(tmp_path):
    # a fixture pins the mechanism; a curation change that moved the count would break this
    rows = load_mapping(_mapping(tmp_path))
    assert len(group_b(rows, cohort_accessions())) == 2   # the two in-cohort rows (approved + preclinical)


def test_group_b_folded_intersection(tmp_path):
    rows = load_mapping(_mapping(tmp_path))
    accs = cohort_accessions()
    # NECTIN4 (Q96NY8) is folded (id 1); the preclinical fixture shares its accession, so both
    # Group B rows resolve to one folded accession
    assert group_b_folded_count(rows, accs, {IN_COHORT}) == 1
    assert group_b_folded_count(rows, accs, set()) == 0    # nothing folded -> nothing fittable


# ── openFDA reconciliation (D-029) — pure given a fixture response ──

def test_new_approval_absent_from_mapping_is_detected(tmp_path):
    rows = load_mapping(_mapping(tmp_path))
    live = ["761137", "999999", "888888"]              # 888888 is a new approval not in the mapping
    diff = reconcile_approvals(rows, live)
    assert "888888" in diff["new_approvals"]
    assert diff["stale_application_numbers"] == []


def test_stale_application_number_is_detected(tmp_path):
    rows = load_mapping(_mapping(tmp_path))
    live = ["761137"]                                  # 999999 no longer resolves -> stale
    diff = reconcile_approvals(rows, live)
    assert "999999" in diff["stale_application_numbers"]
    assert diff["new_approvals"] == []
