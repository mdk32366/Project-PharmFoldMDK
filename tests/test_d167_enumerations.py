"""E1 / E2 / E3 — the three enumerations (AMENDMENT 2 §5). Read-only, tests first.

⚠ These rectify what the R1-R4 read left unmeasured. None is a pass/fail gate EXCEPT E3:

    E1  MUC16 (Q8WXI7) rows BY STATUS, whole-protein and tile identity, run label named incl. (absent)
    E2  the three `pending` run-1 accessions NAMED, and the 2 `failed` confirmed as P11717 / P55073
    E3  which of the 82 cohort accessions lack a complete tranche-0 row -- NAMED, not counted

⚠⚠ E3's stop condition: if the accessions lacking a complete tranche-0 row are not exactly
{P11717, Q8WXI7, Q9NYQ8}, that is a FINDING and Phase 1 does not start in this tunnel. The cohort
account would then be wrong in a way that bears on C3, and C3 gates P2.

⚠ E1 does NOT reopen R4: R4's verdict is ruled (F-082) and is not contingent on it.
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
SCRIPT = REPO / "scripts" / "d167_enumerations.py"

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bALTER\s+TABLE\b|\bCREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX|SCHEMA|EXTENSION)\b"
    r"|\bDROP\s+(?:TABLE|INDEX|SCHEMA)\b", re.I)


def _module():
    name = "scripts.d167_enumerations"
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


# -- 1. the pre-registered set and the stop condition ---------------------------------------------

def test_e3_expects_exactly_the_three_named_accessions():
    r = _module()
    assert r.E3_EXPECTED == ("P11717", "Q8WXI7", "Q9NYQ8")


def test_e3_verdict_stops_when_the_set_differs_and_does_not_when_it_matches():
    """⚠⚠ A-017: the stop is shown capable of firing, in both directions and on a near miss."""
    r = _module()
    ok = r.e3_verdict(["P11717", "Q8WXI7", "Q9NYQ8"])
    assert ok["stop"] is False and ok["matches"] is True
    # order must not matter
    assert r.e3_verdict(["Q9NYQ8", "P11717", "Q8WXI7"])["stop"] is False
    # one extra accession is a finding
    extra = r.e3_verdict(["P11717", "Q8WXI7", "Q9NYQ8", "P04626"])
    assert extra["stop"] is True and extra["unexpected"] == ["P04626"]
    # one missing accession is a finding
    missing = r.e3_verdict(["P11717", "Q8WXI7"])
    assert missing["stop"] is True and missing["absent_from_reading"] == ["Q9NYQ8"]
    # the empty reading is a finding, not a pass
    assert r.e3_verdict([])["stop"] is True


def test_the_cohort_roster_is_read_from_the_committed_file_with_its_documented_format():
    """⚠ `ACCESSION  SYMBOL`, comments skipped. Reading it naively yields 86 rows and zero overlap —
    Code measured exactly that before reading the header."""
    r = _module()
    roster = r.cohort_accessions()
    assert len(roster) == 82 and len(set(roster)) == 82
    assert "P04626" in roster and "Q8WXI7" in roster
    assert not [a for a in roster if a.startswith("#") or " " in a]


# -- 2. keys, counts, and the defect class --------------------------------------------------------

def test_every_reading_states_its_key():
    r = _module()
    for name in ("E1", "E2", "E3"):
        assert name in r.KEYS and len(r.KEYS[name]) > 20


def test_no_reading_derives_a_count_from_a_list_length():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.collect))
    assert "len(" not in code, "collect() takes a length where a count belongs"


def test_the_reading_queries_are_counts_or_named_enumerations_and_are_not_capped():
    r = _module()
    for name in ("E1_SQL", "E2_SQL", "E3_SQL"):
        sql = getattr(r, name)
        assert "LIMIT" not in sql.upper(), f"{name} is capped; a named enumeration is never truncated"
    assert "count(*)" in r.E1_SQL and "count(*)" in r.E2_SQL


def test_e1_names_the_absent_run_label_rather_than_dropping_it():
    """⚠ F-081: an absent run label is a category. E1 must be able to show a MUC16 row that carries
    no generation at all."""
    r = _module()
    assert "coalesce(j.inference_settings->>'run', '(absent)')" in r.E1_SQL


# -- 3. read-only, ASCII, evidence ----------------------------------------------------------------

def test_the_script_executes_no_mutation():
    from test_d159_enqueue_identity import _code_only

    _module()
    hit = _MUTATING.search(_code_only(SCRIPT.read_text(encoding="utf-8")))
    assert hit is None, f"the enumerations execute a mutation: {hit.group(0)!r}"


def test_it_reads_only_through_the_read_only_helper_with_role_then_identity():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    assert "read_only_transaction(eng)" in inspect.getsource(r.main)
    code = _code_only(inspect.getsource(r.collect))
    assert code.index("role_preamble(conn)") < code.index("assert_campaign_target(conn)")


def test_printed_output_is_ascii_on_the_printed_bytes(capsys):
    r = _module()
    r.render({"role": {"session_user": "u§"}, "identity": {"cluster_marker": "k"},
              "readings": {"E1": {"total": 0, "by_status": {}},
                           "E2": {"by_status": {}, "failed_accessions": [], "pending_accessions": []},
                           "E3": {"missing": [], "verdict": {"stop": True, "matches": False,
                                                             "unexpected": [], "absent_from_reading": [],
                                                             "meaning": "none"}}},
              "keys": r.KEYS})
    printed = capsys.readouterr().out
    assert printed and all(ord(ch) < 128 for ch in printed)
    assert "\\xa7" in printed


def test_the_output_is_written_once_with_its_sha256():
    src = SCRIPT.read_text(encoding="utf-8")
    _module()
    assert "write_state(" in src and 'print(f"sha256  : {sha}")' in src


# -- 4. postgres ----------------------------------------------------------------------------------

def _seed(conn, *, muc16_pending: bool = True, cohort_complete_extra: bool = False,
          muc16_unlabelled_tile: bool = False):
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from test_d166_collapse_guards import _seed_population

    conn.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
    conn.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"), {"c": LIVE_CLUSTER_ID})
    _seed_population(conn, CENSUS_FLOOR)

    def job(job_id, acc, tranche, status, settings):
        pdb = f"/data/artifacts/{job_id}/s.pdb" if status == "complete" else None
        conn.execute(text(
            "INSERT INTO protein_analyses (id, input_type, input_value, cohort_tranche, metadata, pdb_path) "
            "VALUES (:a, 'uniprot', :v, :t, '{}', :p)"), {"a": job_id, "v": acc, "t": tranche, "p": pdb})
        conn.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (:j, :a, :s, 1, CAST(:i AS jsonb))"),
            {"j": job_id, "a": job_id, "s": status, "i": json.dumps(settings)})

    whole = {"run": 1}
    # the 82 cohort accessions, complete, EXCEPT the three that are expected to be missing
    from scripts.d167_enumerations import E3_EXPECTED, cohort_accessions
    for n, acc in enumerate(cohort_accessions()):
        if acc in E3_EXPECTED:
            # P11717 failed; the two mucins never folded -> seeded pending
            job(600000 + n, acc, 0, "failed" if acc == "P11717" else "pending", whole)
        else:
            job(600000 + n, acc, 0, "complete", whole)
    if cohort_complete_extra:
        # ⚠ a fourth cohort accession with no complete row: E3 must then STOP
        job(690001, "P04626-X", 0, "pending", whole)
        conn.execute(text("UPDATE jobs SET status = 'pending' WHERE analysis_id = ("
                          "SELECT id FROM protein_analyses WHERE input_value = 'P04626' LIMIT 1)"))

    # census side: MUC16's rows
    if muc16_pending:
        job(650001, "Q8WXI7", 5, "pending", whole)
    if muc16_unlabelled_tile:
        job(650002, "Q8WXI7", 5, "complete",
            {"parent_job_id": 650001, "tile_index": 0, "tile_start": 1, "tile_end": 1656})
    # the other run-1 non-complete rows F-078 recorded: P55073 failed, two more pending
    job(660001, "P55073", 3, "failed", whole)
    job(660002, "P70001", 2, "pending", whole)
    job(660003, "P70002", 2, "pending", whole)


@pytest.fixture
def enum_db(pre_0014):
    return pre_0014


def _run(engine, tmp_path):
    r = _module()
    out = tmp_path / "enumerations.json"
    rc = r.main(["--url", engine.url.render_as_string(hide_password=False), "--out", str(out)])
    return rc, json.loads(out.read_text(encoding="utf-8"))


@pytest.mark.postgres
def test_e3_passes_when_exactly_the_three_lack_a_complete_cohort_row(enum_db, tmp_path):
    with enum_db.begin() as c:
        _seed(c)
    rc, state = _run(enum_db, tmp_path)
    assert rc == 0
    e3 = state["readings"]["E3"]
    assert sorted(e3["missing"]) == ["P11717", "Q8WXI7", "Q9NYQ8"]
    assert e3["verdict"]["stop"] is False


@pytest.mark.postgres
def test_e3_STOPS_when_a_fourth_cohort_accession_lacks_a_complete_row(enum_db, tmp_path):
    """⚠⚠ The stop condition, shown firing. Phase 1 must not start in this tunnel."""
    with enum_db.begin() as c:
        _seed(c, cohort_complete_extra=True)
    rc, state = _run(enum_db, tmp_path)
    assert rc == 2
    e3 = state["readings"]["E3"]
    assert e3["verdict"]["stop"] is True
    assert "P04626" in e3["verdict"]["unexpected"]


@pytest.mark.postgres
def test_e1_reports_muc16_by_status_and_identity_branch(enum_db, tmp_path):
    with enum_db.begin() as c:
        _seed(c, muc16_unlabelled_tile=True)
    rc, state = _run(enum_db, tmp_path)
    e1 = state["readings"]["E1"]
    assert e1["total"] == 3, "the cohort-side pending row, the census pending row, and the tile"
    # ⚠ the grouping carries cohort_tranche, so the cohort-side and census-side pending rows are
    # SEPARATE cells. Collapsing them here would hide which population each row belongs to.
    cells = {(b["status"], b["identity"], b["run_label"], b["cohort_tranche"]): b["count"]
             for b in e1["by_status"]}
    assert cells[("pending", "whole_protein", "1", 0)] == 1, "the cohort-side row"
    assert cells[("pending", "whole_protein", "1", 5)] == 1, "the census-side row"
    assert cells[("complete", "tile", "(absent)", 5)] == 1, (
        "an unlabelled tile is named, not dropped: F-081's category")


@pytest.mark.postgres
def test_e1_shows_muc16_has_no_complete_whole_protein_row(enum_db, tmp_path):
    """⚠ This is what F-082 sub-question 1 asks. It does NOT reopen R4."""
    with enum_db.begin() as c:
        _seed(c)
    _, state = _run(enum_db, tmp_path)
    complete_whole = [b for b in state["readings"]["E1"]["by_status"]
                      if b["status"] == "complete" and b["identity"] == "whole_protein"]
    assert complete_whole == []


@pytest.mark.postgres
def test_e2_names_the_pending_and_confirms_the_failed(enum_db, tmp_path):
    with enum_db.begin() as c:
        _seed(c)
    _, state = _run(enum_db, tmp_path)
    e2 = state["readings"]["E2"]
    assert sorted(e2["failed_accessions"]) == ["P11717", "P55073"]
    assert "Q8WXI7" in e2["pending_accessions"], (
        "MUC16's census row is pending in this fixture, so E2 must name it")
    # ⚠⚠ ROWS are not ACCESSIONS. MUC16 holds a pending row on BOTH sides, so 5 rows resolve to 4
    # distinct accessions. A test that asserted these equal would be the session's defect class in
    # the instrument written to enumerate — CI caught exactly that here.
    assert e2["by_status"]["pending"] == 5, "rows"
    assert e2["distinct_accessions_by_status"]["pending"] == 4, "distinct accessions"
    assert len(e2["pending_accessions"]) == e2["distinct_accessions_by_status"]["pending"]


@pytest.mark.postgres
def test_the_enumerations_execute_no_mutation_and_open_read_only(enum_db, tmp_path):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    with enum_db.begin() as c:
        _seed(c)
    seen: list[str] = []

    def spy(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        rc, _ = _run(enum_db, tmp_path)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    assert rc == 0
    assert any(s.strip() == "SET TRANSACTION READ ONLY" for s in seen)
    assert not [s for s in seen if _MUTATING.search(s)]


from test_d166_collapse_guards import pre_0014  # noqa: E402,F401  (fixture)
