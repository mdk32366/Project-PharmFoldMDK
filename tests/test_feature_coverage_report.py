"""TASK D — `scripts/feature_coverage_report.py` (ORDERS-Code-2026-09-17-TASK-D §4). Tests first.

⚠⚠ The defect this script must not reproduce. `census_profile_statuses`
(`app/census_profile_read.py:127-129`) tests `_incommensurable_assembly` FIRST and `continue`s, so an
assembled parent or tile window displays `refused_assembled_incommensurable` whether or not it has a
feature row. The Planner's lost CSV did not model that, which is why its 777 overstates the display gap.
So "has no feature row" (C1a) and "would gain a rendered profile" (C1c) are DIFFERENT quantities:

    C1a  census representatives with no `protein_features` row
    C1b  of those, how many already refuse as assembled  -> extraction changes nothing visible
    C1c  C1a - C1b                                        -> ⚠ the ONLY true coverage gap

⚠ There is no §1 table to reproduce: the source CSV is gone (RECONSTRUCTION §1). The output IS the
measurement, and `777` is a historical quotation this script never reconciles against. The one surviving
expectation is `C1a >= 773`; SMALLER is a finding.

⚠ A-017: every assertion below is shown capable of failing on a fixture that makes it fail.
⚠ RED AT THE ASSERTION: the module is resolved through `_module()`, which asserts it exists.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import re
from pathlib import Path

import pytest
from sqlalchemy import text

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "feature_coverage_report.py"

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bALTER\s+TABLE\b|\bCREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX|SCHEMA|EXTENSION)\b"
    r"|\bDROP\s+(?:TABLE|INDEX|SCHEMA)\b", re.I)


def _module():
    name = "scripts.feature_coverage_report"
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


# -- 1. one home: the representative rule and the refusal are IMPORTED, never re-implemented -----

def test_the_representative_rule_is_imported_from_app_reads():
    """⚠ ORDERS §4.2 item 6. A second picker is `F-052`'s shape."""
    from app.reads import choose_census_representative

    r = _module()
    assert r.choose_census_representative is choose_census_representative
    src = SCRIPT.read_text(encoding="utf-8")
    assert "def choose_census_representative" not in src, "the picker is re-implemented here"


def test_the_short_circuit_predicate_is_imported_not_copied():
    """⚠⚠ The C1b test must ask the SAME question the page asks, or the report describes a rule the
    site does not follow."""
    from app.census_profile_read import _incommensurable_assembly

    r = _module()
    assert r._incommensurable_assembly is _incommensurable_assembly
    src = SCRIPT.read_text(encoding="utf-8")
    assert "def _incommensurable_assembly" not in src, "the refusal predicate is re-implemented here"


# -- 2. the arithmetic and the keys ---------------------------------------------------------------

def test_c1c_is_c1a_minus_c1b_and_is_named_the_only_coverage_gap():
    r = _module()
    assert r.c1c(773, 141) == 632
    doc = (inspect.getdoc(r.c1c) or "") + r.KEYS["C1c"]
    assert "only" in doc.lower() and "gap" in doc.lower()


def test_c5_can_be_read_alone_so_the_mandatory_pause_is_real():
    """⚠⚠ ORDERS §4 item 2: C5 is reported BEFORE C1 runs, because C5 can invalidate C1's
    expectation. A pause that still computes C1 first is not a pause."""
    r = _module()
    assert r.parse_sections("C5") == ["C5"]
    assert r.parse_sections("C1,C2,C3,C4") == ["C1", "C2", "C3", "C4"]
    assert r.parse_sections("all") == ["C5", "C1", "C2", "C3", "C4"]
    with pytest.raises(SystemExit):
        r.parse_sections("C9")


def test_every_reading_states_its_key():
    """⚠ ORDERS §4.2 item 7: a bare number is not a C-reading."""
    r = _module()
    for name in ("C1a", "C1b", "C1c", "C2", "C3", "C4", "C5"):
        assert name in r.KEYS and len(r.KEYS[name]) > 20, f"{name} has no stated key"


def test_the_only_surviving_expectation_is_the_c1a_floor_and_777_is_never_an_expectation():
    """⚠⚠ ORDERS §4.3: `777` is a historical quotation. The script must not reconcile against it."""
    r = _module()
    assert r.C1A_FLOOR == 773
    assert r.c1a_verdict(773)["finding"] is False
    assert r.c1a_verdict(800)["finding"] is False
    v = r.c1a_verdict(772)
    assert v["finding"] is True and "773" in v["meaning"]
    code = SCRIPT.read_text(encoding="utf-8")
    assert "777" not in code, "the lost table's figure is quoted as if it were live"


# -- 3. the defect class: no count comes from a list length ---------------------------------------

def test_no_reading_derives_a_count_from_a_list_length():
    """⚠⚠ The session's shared defect class, which the R1-R4 instrument caught inside its own draft
    (`len(R4_ACCESSIONS)`)."""
    from test_d159_enqueue_identity import _code_only

    r = _module()
    for fn in (r.collect, r.representative_readings):
        code = _code_only(inspect.getsource(fn))
        assert "len(" not in code, f"{fn.__name__} takes a length where a count belongs"


def test_c4_branches_are_counted_not_subtracted():
    """⚠ ORDERS §4.2 item 10: each branch its own count, never a subtraction from a total."""
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.representative_readings))
    assert " - " not in code, "a C4 branch is derived by arithmetic"


def test_a_capped_list_is_labelled_capped_and_carries_a_count_it_did_not_derive():
    r = _module()
    d = r.capped_list("C2 ids", count=120, rows=[1, 2, 3], cap=3)
    assert d["capped"] is True and d["count"] == 120 and d["rows_shown"] == 3
    assert "CAPPED" in r.format_capped(d)
    assert r.capped_list("C2 ids", count=2, rows=[1, 2], cap=50)["capped"] is False
    # capped BELOW the cap too: fewer rows than the count is still capped
    assert r.capped_list("C2 ids", count=9, rows=[1], cap=50)["capped"] is True


# -- 4. read-only, ASCII, evidence ----------------------------------------------------------------

def test_the_script_executes_no_mutation():
    from test_d159_enqueue_identity import _code_only

    _module()
    hit = _MUTATING.search(_code_only(SCRIPT.read_text(encoding="utf-8")))
    assert hit is None, f"the coverage report executes a mutation: {hit.group(0)!r}"


def test_it_reads_only_through_the_read_only_helper_with_role_then_identity():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    assert "read_only_transaction(eng)" in inspect.getsource(r.main)
    code = _code_only(inspect.getsource(r.collect))
    assert code.index("role_preamble(conn)") < code.index("assert_campaign_target(conn)")


def test_printed_output_is_ascii_asserted_on_the_printed_bytes(capsys):
    """⚠⚠ ORDERS §4.2 item 5. A source-only ASCII check is not an output ASCII check: only the
    printed-byte assertion caught `core.db_role.format_preamble`'s section sign, and only in CI."""
    r = _module()
    r.render({"role": {"session_user": "u§", "current_user": "c"},
              "identity": {"cluster_marker": "k", "transaction_read_only": "on"},
              "readings": {"C5": {"v1_rows": 2690, "in_table": 0, "sample": {"checked": 0,
                                                                            "equal": 0,
                                                                            "differing": []}},
                           "C1a": 773, "C1b": 141, "C1c": 632,
                           "C1a_verdict": {"finding": False, "meaning": "at or above the floor"},
                           "C2": {"count": 0, "ids": []}, "C3": 0,
                           "C4": {"assembled": 45, "tiles_only": 0, "single-pass": 3418, "mucin": 3}},
              "diagnostics": {"C2_ids": r.capped_list("C2 ids", 0, [], 50)},
              "keys": r.KEYS})
    printed = capsys.readouterr().out
    assert printed, "render printed nothing"
    assert all(ord(ch) < 128 for ch in printed), "non-ASCII character in the printed output"
    assert "\\xa7" in printed, "a non-ASCII character was dropped rather than escaped"


def test_the_output_is_written_once_with_its_sha256():
    src = SCRIPT.read_text(encoding="utf-8")
    _module()
    assert "write_state(" in src, "the write-once helper is not reused (one home: d167_read_state)"
    assert 'print(f"sha256  : {sha}")' in src


# -- 5. postgres: the short-circuit modelled, on data that makes each assertion fail --------------

def _seed(conn, *, assembled_with_features: bool = False, stale_representative: bool = False,
          cohort_gap: bool = False):
    """A miniature census: one single-pass row WITH features, one single-pass row WITHOUT,
    one assembled parent WITHOUT features (the C1b case), plus a cohort row."""
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from test_d166_collapse_guards import _seed_population

    conn.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
    conn.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"), {"c": LIVE_CLUSTER_ID})
    _seed_population(conn, CENSUS_FLOOR)

    def analysis(aid, acc, tranche, meta, pdb="/data/artifacts/x/structure.pdb"):
        conn.execute(text(
            "INSERT INTO protein_analyses (id, input_type, input_value, cohort_tranche, metadata, pdb_path) "
            "VALUES (:a, 'uniprot', :v, :t, CAST(:m AS jsonb), :p)"),
            {"a": aid, "v": acc, "t": tranche, "m": json.dumps(meta), "p": pdb})
        conn.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (:j, :a, 'complete', 1, CAST(:i AS jsonb))"),
            {"j": aid, "a": aid, "i": json.dumps({"run": 1})})

    def features(aid, mean_plddt=70.0):
        conn.execute(text(
            "INSERT INTO protein_features (analysis_id, ecd_length, mean_plddt_ecd, sasa_normalized, "
            "radius_of_gyration, largest_patch_fraction, membrane_proximal_plddt, extraction_outcome) "
            "VALUES (:a, 300, :m, 120.0, 1.5, 0.4, 65.0, 'ok')"), {"a": aid, "m": mean_plddt})

    analysis(800001, "P80001", 1, {})              # single-pass, features -> neither C1a nor C1c
    features(800001)
    analysis(800002, "P80002", 1, {})              # single-pass, NO features -> C1a and C1c
    analysis(800003, "P80003", 2, {"hold48_kind": "parent", "stitched": True},
             pdb="/data/artifacts/800003/stitched.pdb")   # assembled parent, NO features -> C1a, C1b
    if assembled_with_features:
        features(800003)                           # ⚠ still C1b: the page never consults the row
    if stale_representative:
        analysis(800004, "P80004", 1, {})
        analysis(800005, "P80004", 1, {})          # same accession, higher id: not the representative
        features(800005)
    analysis(700001, "P70001", 0, {})              # cohort row
    if not cohort_gap:
        features(700001)


@pytest.fixture
def cov_db(pre_0014, monkeypatch):
    """⚠ The floor is a claim about PRODUCTION (C1a >= 773). A miniature fixture is always below it,
    so the floor is neutralised here and exercised on its own in the two floor tests below — rather
    than left to make every other test read as a finding."""
    r = _module()
    monkeypatch.setattr(r, "C1A_FLOOR", 0)
    return pre_0014


def _run(engine, tmp_path, sections: str = "all", name: str = "coverage.json"):
    r = _module()
    out = tmp_path / name
    rc = r.main(["--url", engine.url.render_as_string(hide_password=False), "--out", str(out),
                 "--sections", sections])
    return rc, json.loads(out.read_text(encoding="utf-8"))


@pytest.mark.postgres
def test_an_assembled_parent_with_no_feature_row_lands_in_c1b_not_c1c(cov_db, tmp_path):
    with cov_db.begin() as c:
        _seed(c)
    rc, state = _run(cov_db, tmp_path)
    assert rc == 0
    rd = state["readings"]
    assert rd["C1a"] == 2, "the single-pass gap and the assembled parent both lack a feature row"
    assert rd["C1b"] == 1, "the assembled parent already refuses; extraction changes nothing for it"
    assert rd["C1c"] == 1, "only the single-pass row would gain a rendered profile"


@pytest.mark.postgres
def test_an_assembled_parent_WITH_features_is_still_c1b_because_the_page_never_reads_the_row(
        cov_db, tmp_path):
    """⚠⚠ The discriminating case. A report that counts feature rows instead of asking the page's
    question would move this row out of C1b, and that is the Planner's CSV error."""
    with cov_db.begin() as c:
        _seed(c, assembled_with_features=True)
    rc, state = _run(cov_db, tmp_path)
    assert rc == 0
    rd = state["readings"]
    assert rd["C1a"] == 1, "the assembled parent now HAS a feature row, so it is not a C1a"
    assert rd["C4"]["assembled"] == 0, "C4 breaks down C1a, which no longer holds the parent"
    assert rd["C1c"] == 1


@pytest.mark.postgres
def test_c2_names_a_stale_representative_with_its_count_and_ids(cov_db, tmp_path):
    with cov_db.begin() as c:
        _seed(c, stale_representative=True)
    rc, state = _run(cov_db, tmp_path)
    assert rc == 0
    c2 = state["readings"]["C2"]
    assert c2["count"] == 1 and c2["ids"] == [800004], (
        "the accession's features hang off 800005 while 800004 is the representative")


@pytest.mark.postgres
def test_c3_counts_the_cohort_gap_and_is_zero_when_there_is_none(cov_db, tmp_path):
    with cov_db.begin() as c:
        _seed(c)
    _, state = _run(cov_db, tmp_path)
    assert state["readings"]["C3"] == 0


@pytest.mark.postgres
def test_c3_is_nonzero_when_a_cohort_row_lacks_features(cov_db, tmp_path):
    """⚠ C3 decides P2, so it must be shown capable of reading non-zero."""
    with cov_db.begin() as c:
        _seed(c, cohort_gap=True)
    _, state = _run(cov_db, tmp_path)
    assert state["readings"]["C3"] == 1


@pytest.mark.postgres
def test_c4_breaks_c1a_down_by_structure_kind_and_keeps_mucin_as_its_own_branch(cov_db, tmp_path):
    """⚠ The picker returns FOUR kinds, not the three the orders name (`app/reads.py:980-997`), and
    `mucin` is exactly MUC16's case (F-082). It is never folded into `single-pass`."""
    with cov_db.begin() as c:
        _seed(c)
    _, state = _run(cov_db, tmp_path)
    c4 = state["readings"]["C4"]
    assert c4["assembled"] == 1 and c4["single-pass"] == 1
    assert set(c4) >= {"assembled", "tiles_only", "single-pass", "mucin"}
    assert sum(c4.values()) == state["readings"]["C1a"], "C4 must partition C1a"


@pytest.mark.postgres
def test_every_c4_branch_is_present_with_a_zero_rather_than_absent(cov_db, tmp_path):
    """⚠⚠ D-027: an absence is a category. A branch that disappears when its count is zero reads as
    'not measured' instead of 'measured none' — which is how a fifth silent category hides."""
    with cov_db.begin() as c:
        _seed(c, assembled_with_features=True)
    _, state = _run(cov_db, tmp_path)
    c4 = state["readings"]["C4"]
    assert c4["assembled"] == 0, "the parent now has features, so this branch is zero — and present"
    assert c4["mucin"] == 0 and c4["tiles_only"] == 0


@pytest.mark.postgres
def test_c5_reports_whether_v1_ever_reached_the_table(cov_db, tmp_path):
    """⚠ The load-bearing reading: the panel reads the TABLE, and v1's manifest records
    `wrote_database_rows: false`."""
    with cov_db.begin() as c:
        _seed(c)
    _, state = _run(cov_db, tmp_path)
    c5 = state["readings"]["C5"]
    assert c5["v1_rows"] > 0, "the v1 artifact's row count comes from the committed artifact"
    assert c5["in_table"] == 0, "none of this fixture's feature rows is a v1 analysis_id"
    assert c5["sample"]["checked"] == 0


@pytest.mark.postgres
def test_a_c1a_below_the_floor_is_a_finding_and_exits_2(cov_db, tmp_path, monkeypatch):
    """⚠ ORDERS §4.3: the floor survives the loss of the table; the old gap figure does not.
    A-017: the floor is shown capable of firing, on a fixture that makes it fire."""
    r = _module()
    monkeypatch.setattr(r, "C1A_FLOOR", 99)
    with cov_db.begin() as c:
        _seed(c)
    rc, state = _run(cov_db, tmp_path)
    assert rc == 2
    v = state["readings"]["C1a_verdict"]
    assert v["finding"] is True and v["floor"] == 99


@pytest.mark.postgres
def test_a_c1a_at_or_above_the_floor_is_not_a_finding_and_exits_0(cov_db, tmp_path, monkeypatch):
    r = _module()
    monkeypatch.setattr(r, "C1A_FLOOR", 1)
    with cov_db.begin() as c:
        _seed(c)
    rc, state = _run(cov_db, tmp_path)
    assert rc == 0 and state["readings"]["C1a_verdict"]["finding"] is False


@pytest.mark.postgres
def test_reading_c5_alone_computes_no_c1_and_writes_its_own_evidence_file(cov_db, tmp_path):
    """⚠⚠ The pause, proven: a C5-only run must not carry C1a/C1b/C1c at all — not even as zeros,
    which would read as 'measured none' when nothing was measured."""
    with cov_db.begin() as c:
        _seed(c)
    rc, state = _run(cov_db, tmp_path, sections="C5", name="c5.json")
    assert rc == 0
    assert "C5" in state["readings"]
    for absent in ("C1a", "C1b", "C1c", "C1a_verdict", "C2", "C3", "C4"):
        assert absent not in state["readings"], f"{absent} was computed during the C5-only pause"
    assert state["sections"] == ["C5"]
    # and the rest runs afterwards, into its OWN file
    rc2, rest = _run(cov_db, tmp_path, sections="C1,C2,C3,C4", name="rest.json")
    assert rc2 == 0 and "C5" not in rest["readings"] and rest["readings"]["C1a"] == 2


@pytest.mark.postgres
def test_the_report_executes_no_mutation_and_opens_read_only(cov_db, tmp_path):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    with cov_db.begin() as c:
        _seed(c)
    seen: list[str] = []

    def spy(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        rc, _ = _run(cov_db, tmp_path)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    assert rc == 0
    assert any(s.strip() == "SET TRANSACTION READ ONLY" for s in seen)
    assert not [s for s in seen if _MUTATING.search(s)]


from test_d166_collapse_guards import pre_0014  # noqa: E402,F401  (fixture)
