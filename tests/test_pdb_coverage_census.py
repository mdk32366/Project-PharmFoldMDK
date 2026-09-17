"""T0 — the PDB coverage census instrument (SPEC v2 §5). OFFLINE. Tests first.

⚠⚠ NO TEST TOUCHES THE NETWORK. Every fixture is a local dict or a temp file, and the instrument's
only source in T0 is a cache directory. T1 is not authorised and no live source is implemented.

⚠ What this instrument does NOT do: compare a structure to a structure. It measures, per accession,
whether a PDB entry maps, whether it overlaps the ECD span WE folded, and by how many residues.

⚠⚠ TWO sum checks, never one: the outcomes sum to 82 for the cohort pass and to 3,467 for the census
pass. A combined check is the error SPEC v2 exists to correct, and the void figure must appear nowhere.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "pdb_coverage_census.py"


def _module():
    name = "scripts.pdb_coverage_census"
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


def _entry(pdb_id="1abc", start=100, end=400, identity=99.0, engineered=0.0, chimera=False,
           method="X-RAY DIFFRACTION", resolution=2.0):
    return {"pdb_id": pdb_id, "chain": "A", "unp_start": start, "unp_end": end,
            "identity": identity, "engineered_fraction": engineered, "is_chimera": chimera,
            "method": method, "resolution": resolution}


# -- 1. the pre-registered policy, fixed before any data ------------------------------------------

def test_the_policy_numbers_are_the_pre_registered_ones():
    r = _module()
    assert r.MIN_OVERLAP_RESIDUES == 50
    assert r.MIN_IDENTITY_PERCENT == 95.0


def test_the_seven_outcomes_exist_and_our_two_are_never_folded_into_the_pdb_s():
    r = _module()
    for name in ("pdb_ecd_overlap", "overlap_below_minimum", "entry_but_no_ecd_overlap",
                 "engineered_construct_only", "no_pdb_entry", "accession_unresolved", "span_unknown"):
        assert name in r.OUTCOMES
    doc = inspect.getdoc(r.classify_accession) or ""
    assert "accession_unresolved" in doc and "span_unknown" in doc


def test_every_outcome_initialises_to_zero_and_none_can_vanish():
    """⚠⚠ D-027 at the reporting surface — the defect the coverage report failed CI on."""
    r = _module()
    tally = r.new_tally()
    assert set(tally) == set(r.OUTCOMES)
    assert all(v == 0 for v in tally.values())


def test_an_outcome_the_code_produces_is_added_never_folded():
    """⚠ SPEC v2 §5 item 2. If `classify_accession` can return it, the tally must carry it."""
    r = _module()
    produced = set(r.OUTCOMES)
    src = inspect.getsource(r.classify_accession)
    returned = set(re.findall(r'return "([a-z_]+)"', src)) | set(
        re.findall(r'outcome = "([a-z_]+)"', src))
    assert returned <= produced, f"an outcome is produced but not tallied: {returned - produced}"


# -- 2. classification, one fixture per named outcome ---------------------------------------------

def test_a_clean_overlap_qualifies():
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[_entry()])
    assert out == "pdb_ecd_overlap"
    assert detail["best"]["overlap"] == 301 and detail["best"]["pdb_id"] == "1abc"


def test_no_span_is_our_condition_not_the_pdb_s():
    r = _module()
    out, detail = r.classify_accession(span=None, entries=[_entry()])
    assert out == "span_unknown"
    assert "our record" in detail["meaning"]


def test_an_unresolved_accession_is_an_instrument_condition():
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=None, unresolved="HTTP 429")
    assert out == "accession_unresolved" and detail["reason"] == "HTTP 429"


def test_no_entry_at_all():
    r = _module()
    out, _ = r.classify_accession(span=(100, 400), entries=[])
    assert out == "no_pdb_entry"


def test_an_entry_that_misses_the_span_entirely():
    """⚠ A cytoplasmic-domain structure is a PDB hit that says nothing about the ECD we folded."""
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[_entry(start=700, end=900)])
    assert out == "entry_but_no_ecd_overlap" and detail["entries_considered"] == 1


def test_an_overlap_shorter_than_the_minimum():
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[_entry(start=80, end=120)])
    assert out == "overlap_below_minimum" and detail["best"]["overlap"] == 21


def test_the_minimum_is_inclusive_at_fifty():
    """⚠ A-017: the boundary is pinned in both directions, so an off-by-one cannot pass silently."""
    r = _module()
    at = r.classify_accession(span=(100, 400), entries=[_entry(start=100, end=149)])
    below = r.classify_accession(span=(100, 400), entries=[_entry(start=100, end=148)])
    assert at[1]["best"]["overlap"] == 50 and at[0] == "pdb_ecd_overlap"
    assert below[1]["best"]["overlap"] == 49 and below[0] == "overlap_below_minimum"


def test_a_chimera_and_a_majority_engineered_overlap_are_disqualified():
    r = _module()
    chimera = r.classify_accession(span=(100, 400), entries=[_entry(chimera=True)])
    engineered = r.classify_accession(span=(100, 400), entries=[_entry(engineered=0.6)])
    assert chimera[0] == "engineered_construct_only"
    assert engineered[0] == "engineered_construct_only"


def test_an_identity_failure_is_its_own_named_outcome_and_is_not_folded():
    """⚠⚠ REPORTED TO THE PLANNER: SPEC v2 §1's seven outcomes have NO home for an entry that
    overlaps well but fails the 95% identity floor. Folding it into `overlap_below_minimum` would
    report an ortholog mismatch as a length problem, and into `no_pdb_entry` would report our filter
    as nature's. It is ADDED as an eighth, named outcome (§5 item 2 permits exactly this)."""
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[_entry(identity=71.0)])
    assert out == "overlap_identity_below_minimum"
    assert out in r.OUTCOMES, "an outcome the code produces must be tallied"
    assert detail["best_rejected"]["identity"] == 71.0


def test_the_best_entry_is_chosen_deterministically():
    """Longest qualifying overlap; tie -> better resolution; tie -> lower PDB id."""
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[
        _entry(pdb_id="3zzz", start=100, end=200),
        _entry(pdb_id="2bbb", start=100, end=300, resolution=1.5),
        _entry(pdb_id="1aaa", start=100, end=300, resolution=2.8),
    ])
    assert out == "pdb_ecd_overlap"
    assert detail["best"]["pdb_id"] == "2bbb", "longest, then the better resolution"
    assert detail["entries_considered"] == 3


def test_a_resolution_tie_falls_to_the_lower_pdb_id():
    r = _module()
    _, detail = r.classify_accession(span=(100, 400), entries=[
        _entry(pdb_id="9xyz", start=100, end=300, resolution=2.0),
        _entry(pdb_id="1abc", start=100, end=300, resolution=2.0),
    ])
    assert detail["best"]["pdb_id"] == "1abc"


def test_method_and_resolution_are_recorded_not_filtered():
    """⚠ SPEC v2 §3 item 5: filtering belongs to step 2."""
    r = _module()
    out, detail = r.classify_accession(span=(100, 400), entries=[
        _entry(method="ELECTRON MICROSCOPY", resolution=7.4)])
    assert out == "pdb_ecd_overlap", "a low-resolution EM entry is NOT filtered out at step 1"
    assert detail["best"]["method"] == "ELECTRON MICROSCOPY" and detail["best"]["resolution"] == 7.4


# -- 3. the two sum checks, and the void figure ---------------------------------------------------

def test_the_two_sum_checks_are_separate_and_each_names_its_population():
    r = _module()
    cohort = r.new_tally()
    cohort["pdb_ecd_overlap"] = 82
    ok = r.sum_check("cohort", cohort, 82)
    assert ok["ok"] is True and ok["expected"] == 82 and ok["population"] == "cohort"
    census = r.new_tally()
    census["no_pdb_entry"] = 3467
    assert r.sum_check("census", census, 3467)["ok"] is True


def test_a_sum_that_misses_its_population_fails():
    r = _module()
    t = r.new_tally()
    t["pdb_ecd_overlap"] = 81
    bad = r.sum_check("cohort", t, 82)
    assert bad["ok"] is False and bad["total"] == 81


def test_the_expected_totals_are_the_two_populations_and_never_their_union():
    r = _module()
    assert r.EXPECTED_TOTALS == {"cohort": 82, "census": 3467}
    assert 3474 not in r.EXPECTED_TOTALS.values(), "the union double-counts the 75"


def test_the_void_figure_appears_nowhere_in_the_instrument():
    """⚠⚠ SPEC v2 §1.1 item 3: `3,385` is void. A test fails if it ever appears."""
    code = SCRIPT.read_text(encoding="utf-8")
    assert "3385" not in code.replace(",", ""), "the void figure is present in the instrument"


def test_the_populations_are_read_from_the_committed_files_and_overlap_is_not_hidden():
    r = _module()
    cohort, census = r.population("cohort"), r.population("census")
    assert len(cohort) == 82 and len(census) == 3467
    shared = set(cohort) & set(census)
    assert len(shared) == 75, "the populations overlap by 75; the instrument must not pretend otherwise"


# -- 4. spans come from our record, and the record is named ---------------------------------------

def test_census_spans_come_from_the_manifest_and_name_their_source():
    r = _module()
    spans = r.spans_for("census")
    assert len(spans) == 3467
    acc, rec = next(iter(spans.items()))
    assert rec["source"].endswith("census_manifest.v7.csv")
    assert rec["start"] <= rec["end"]


def test_cohort_spans_come_from_the_cohort_ecd_record_and_name_their_source():
    r = _module()
    spans = r.spans_for("cohort")
    assert spans["P04626"]["source"].endswith("cohort_82_ecd.csv")
    assert spans["P04626"]["end"] > spans["P04626"]["start"]


def test_an_accession_with_no_held_span_is_span_unknown_rather_than_a_guess():
    r = _module()
    tally, records = r.run_pass("cohort", ["P-NOSPAN"], spans={}, source=r.DictSource({}), delay=0)
    assert tally["span_unknown"] == 1
    assert records[0]["outcome"] == "span_unknown"


# -- 5. the defect class, capped lists, cache labelling, partial runs ------------------------------

def test_no_tally_is_derived_from_a_list_length():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.run_pass))
    assert "len(" not in code, "run_pass takes a length where a tally belongs"


def test_a_capped_list_is_labelled_capped():
    r = _module()
    d = r.capped_list("examples", count=900, rows=[1, 2], cap=2)
    assert d["capped"] is True and d["count"] == 900
    assert "CAPPED" in r.format_capped(d)


def test_a_cache_hit_is_labelled_as_one_in_the_artifact():
    r = _module()
    src = r.DictSource({"P1": {"entries": [_entry()], "cache_hit": True, "release": "2026-09-01"}})
    _, records = r.run_pass("cohort", ["P1"], spans={"P1": {"start": 100, "end": 400, "source": "x"}},
                            source=src, delay=0)
    assert records[0]["cache_hit"] is True


def test_a_rate_limit_is_a_recorded_outcome_not_a_silent_retry():
    r = _module()
    src = r.DictSource({"P1": {"error": "HTTP 429"}})
    tally, records = r.run_pass("cohort", ["P1"],
                                spans={"P1": {"start": 100, "end": 400, "source": "x"}},
                                source=src, delay=0)
    assert tally["accession_unresolved"] == 1
    assert records[0]["detail"]["reason"] == "HTTP 429"


def test_a_partial_pass_reports_as_partial_with_how_far_it_got():
    r = _module()
    state = r.pass_state("census", tally=r.new_tally(), read=10, population=3467,
                         release="2026-09-01")
    assert state["partial"] is True and state["read"] == 10 and state["population"] == 3467
    full = r.pass_state("cohort", tally=r.new_tally(), read=82, population=82, release="x")
    assert full["partial"] is False


def test_resume_skips_what_is_already_held_and_says_how_many(tmp_path):
    """⚠ SPEC v2 §5 item 7: a killed tranche restarts without re-reading what it holds."""
    r = _module()
    progress = tmp_path / "cohort.partial.jsonl"
    progress.write_text(json.dumps({"accession": "P1", "outcome": "no_pdb_entry",
                                    "detail": {}, "cache_hit": False}) + "\n", encoding="utf-8")
    held = r.load_progress(progress)
    assert set(held) == {"P1"}
    src = r.DictSource({"P2": {"entries": []}})
    tally, records = r.run_pass("cohort", ["P1", "P2"],
                                spans={"P1": {"start": 1, "end": 100, "source": "x"},
                                       "P2": {"start": 1, "end": 100, "source": "x"}},
                                source=src, delay=0, held=held)
    assert tally["no_pdb_entry"] == 2, "the held record still counts toward the tally"
    assert [rec["accession"] for rec in records if rec.get("resumed")] == ["P1"]


def test_the_re_read_of_an_accession_is_marked_as_a_re_read():
    """⚠ SPEC v2 §1.1 item 4: the 75 and the 300 are read twice, and the artifact says so."""
    r = _module()
    src = r.DictSource({"P04626": {"entries": []}})
    _, records = r.run_pass("census", ["P04626"],
                            spans={"P04626": {"start": 1, "end": 100, "source": "x"}},
                            source=src, delay=0, already_read_in={"cohort"})
    assert records[0]["re_read_of"] == ["cohort"]


# -- 6. output: ASCII on the printed bytes, write-once, manifest ----------------------------------

def test_printed_output_is_ascii_on_the_printed_bytes(capsys):
    r = _module()
    tally = r.new_tally()
    tally["pdb_ecd_overlap"] = 1
    r.render({"pass": "cohort", "tally": tally, "sum_check": r.sum_check("cohort", tally, 1),
              "read": 1, "population": 1, "partial": False, "release": "2026-09-01§",
              "policy": r.policy_block(), "examples": r.capped_list("examples", 1, [], 5)})
    printed = capsys.readouterr().out
    assert printed and all(ord(ch) < 128 for ch in printed)
    assert "\\xa7" in printed


def test_the_artifact_is_written_once_with_its_sha256_and_pins_the_hash_seed(tmp_path):
    r = _module()
    state = {"pass": "cohort", "tally": r.new_tally()}
    sha = r.write_artifact(state, tmp_path / "t.json")
    assert len(sha) == 64
    written = json.loads((tmp_path / "t.json").read_text(encoding="utf-8"))
    assert "PYTHONHASHSEED" in written["manifest"]
    assert written["manifest"]["spec"].endswith("tranches-v2.md")
    with pytest.raises(SystemExit):
        r.write_artifact(state, tmp_path / "t.json")


def test_no_network_client_exists_in_the_instrument():
    """⚠⚠ T0 is offline and T1 is NOT authorised. A live client must not be present to be called
    by accident."""
    code = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("import requests", "urllib.request", "httpx", "http.client", "socket."):
        assert forbidden not in code, f"a network client is present in a T0-only instrument: {forbidden}"


def test_the_cli_refuses_to_run_a_tranche_that_is_not_authorised():
    r = _module()
    with pytest.raises(SystemExit):
        r.main(["--pass", "cohort", "--source", "nonexistent-dir"])
