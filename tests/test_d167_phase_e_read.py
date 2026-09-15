"""D-167 Phase E read (ORDERS Amendment 8, A8.3) — one read-only tunnel, outcomes pre-registered.

⚠⚠ Why this exists. A8.2 (Planner error 7) found that the E.1 witness "census untouched: 3,651" expected an
invariance the sitting was designed to break: the collapse deleted rows INSIDE the counted key
(`run = '1' AND complete`). `data/control/f078/f078_scope.json` measures job 3696 there; 3693 and 3695 are
inferred. So the census is read once more, and its reading is classified against a table fixed BEFORE the
read — all outcomes at equal prominence:

    3,648           all three dropped rows were in the key          -> expected, recorded
    3,649 / 3,650   one or two unsampled drops carried no run '1'   -> named category, not a stop
    3,651           no drop in the key, contradicting 3696          -> finding, STOP
    anything else   rows outside the collapse changed               -> finding, STOP

⚠ RED AT THE ASSERTION: the module under test is resolved through `_module()`, which asserts it exists.

⚠ The postgres half shrinks the baseline by monkeypatching the module's constants — the classification is
RELATIVE to the baseline, and that is what is proven: baseline-3 passes, baseline fails.
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
SCRIPT = REPO / "scripts" / "d167_phase_e_read.py"
COLLAPSE_LOG = REPO / "data" / "control" / "d167" / "phase_d" / "06-collapse-dry.txt"

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bALTER\s+TABLE\b|\bCREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX|SCHEMA|EXTENSION)\b"
    r"|\bDROP\s+(?:TABLE|INDEX|SCHEMA)\b", re.I)


def _module():
    name = "scripts.d167_phase_e_read"
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


# ── 1. the pre-registered table, exactly ────────────────────────────────────────────────────────

def test_the_expected_reading_is_baseline_minus_three_and_does_not_stop():
    r = _module()
    v = r.classify_census(3648)
    assert v["verdict"] == "expected" and v["stop"] is False


@pytest.mark.parametrize("n, outside", [(3649, 1), (3650, 2)])
def test_one_or_two_drops_outside_the_key_is_a_named_category_not_a_stop(n, outside):
    r = _module()
    v = r.classify_census(n)
    assert v["verdict"] == "named_category" and v["stop"] is False
    assert v["drops_outside_key"] == outside
    assert v["candidates"] == [3693, 3695], "3696 is measured in the key; only the unsampled drops can be outside"


def test_the_unchanged_baseline_is_a_finding_and_stops():
    """⚠ 3,651 would mean no dropped row was in the key — contradicting job 3696's measured run '1'."""
    r = _module()
    v = r.classify_census(3651)
    assert v["verdict"] == "finding" and v["stop"] is True
    assert "3696" in v["meaning"]


@pytest.mark.parametrize("n", [3647, 3652, 3600, 0])
def test_any_other_reading_is_a_finding_and_stops(n):
    r = _module()
    v = r.classify_census(n)
    assert v["verdict"] == "finding" and v["stop"] is True


def test_the_constants_are_the_evidence_not_a_guess():
    """The baseline is F-078's measured census; the collapse ids are the ones 06-collapse-dry.txt names;
    job 3696 is the one f078_scope.json measures inside the key."""
    r = _module()
    assert r.BASELINE_CENSUS == 3651
    log = COLLAPSE_LOG.read_text(encoding="utf-8")
    assert tuple(int(x) for x in re.findall(r"KEEP job (\d+)", log)) == r.KEEP_JOBS == (3673, 3674, 3675)
    assert tuple(int(x) for x in re.findall(r"DROP job (\d+)", log)) == r.DROP_JOBS == (3693, 3695, 3696)
    scope = json.loads((REPO / "data" / "control" / "f078" / "f078_scope.json").read_text(encoding="utf-8"))
    in_key = sorted(row["job"] for row in scope
                    if row.get("job") in r.DROP_JOBS and row.get("run") == "1" and row.get("status") == "complete")
    assert tuple(in_key) == r.DROPS_MEASURED_IN_KEY == (3696,)
    assert r.NONCOMPLETE_BY_STATUS == {"failed": 2, "pending": 3}
    assert set(r.FAILED_ACCESSIONS) == {"P11717", "P55073"}


# ── 2. read-only, role first, identity second, evidence kept ────────────────────────────────────

def test_the_script_executes_no_mutation():
    from test_d159_enqueue_identity import _code_only

    _module()
    hit = _MUTATING.search(_code_only(SCRIPT.read_text(encoding="utf-8")))
    assert hit is None, f"the Phase E read executes a mutation: {hit.group(0)!r}"


def test_main_reads_only_through_the_read_only_helper():
    r = _module()
    src = inspect.getsource(r.main)
    assert "read_only_transaction(eng)" in src
    assert "eng.begin()" not in src and "eng.connect()" not in src


def test_role_then_identity_then_the_first_reported_read():
    from test_d159_enqueue_identity import _code_only

    _module()
    code = _code_only(SCRIPT.read_text(encoding="utf-8"))
    role, ident = code.index("role_preamble(conn)"), code.index("assert_campaign_target(conn)")
    first_read = code.index("inference_settings->>'run'")
    assert role < ident < first_read


def test_the_output_is_written_once_with_its_sha256_and_labels_the_url_username():
    r = _module()
    assert r.OUT == REPO / "data" / "control" / "d167" / "phase_e_read.json"
    src = SCRIPT.read_text(encoding="utf-8")
    assert "write_state(" in src, "the write-once helper is not reused (one home: d167_read_state)"
    assert 'print(f"sha256  : {sha}")' in src
    assert '"url_username": eng.url.username' in src


def test_the_script_prints_ascii_only():
    """⚠ A7.4: printed output from Phase D scripts is made ASCII. A new script starts that way, so a
    PowerShell pipe under cp1252 cannot turn its evidence into a traceback."""
    from test_d159_enqueue_identity import _code_only

    _module()
    code = _code_only(SCRIPT.read_text(encoding="utf-8"))
    bad = sorted({ch for ch in code if ord(ch) > 127})
    assert not bad, f"non-ASCII characters in executable code: {bad}"


# ── 3. postgres: the read, end to end, on seeded data ───────────────────────────────────────────

SMALL_BASELINE = 12            # expected reading 9 = baseline - 3


def _seed(conn, complete_whole: int, *, extra_keep_dup: bool = False, drop_row_present: bool = False):
    """Marker + floor; the three keep tiles (complete, run 1); `complete_whole` whole-protein run-1 rows;
    the five non-complete run-1 rows (2 failed incl. P11717/P55073, 3 pending)."""
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from test_d166_collapse_guards import _seed_population

    conn.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
    conn.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"), {"c": LIVE_CLUSTER_ID})
    _seed_population(conn, CENSUS_FLOOR)

    def job(job_id, acc, status, settings, pdb):
        conn.execute(text(
            "INSERT INTO protein_analyses (id, input_type, input_value, metadata, pdb_path) "
            "VALUES (:a, 'uniprot', :v, '{}', :p)"), {"a": job_id, "v": acc, "p": pdb})
        conn.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (:j, :a, :s, 1, CAST(:i AS jsonb))"),
            {"j": job_id, "a": job_id, "s": status, "i": json.dumps(settings)})

    for k, (job_id, parent) in enumerate(((3673, 2817), (3674, 2837), (3675, 2917))):
        job(job_id, f"Q-TILE{k}", "complete",
            {"run": "1", "parent_job_id": parent, "tile_index": k, "tile_start": 1, "tile_end": 1656},
            f"/data/artifacts/{job_id}/structure.pdb")
    for n in range(complete_whole):
        job(6000 + n, f"P9{n:04d}", "complete", {"run": "1", "ecd_start": 1, "ecd_end": 30},
            f"/data/artifacts/{6000 + n}/structure.pdb")
    for job_id, acc, status in ((7001, "P11717", "failed"), (7002, "P55073", "failed"),
                                (7003, "P70003", "pending"), (7004, "P70004", "pending"),
                                (7005, "P70005", "pending")):
        job(job_id, acc, status, {"run": "1"}, None)
    if drop_row_present:
        job(3696, "Q-TILE2", "complete",
            {"run": "1", "parent_job_id": 2917, "tile_index": 0, "tile_start": 1, "tile_end": 1656},
            "/data/artifacts/3696/structure.pdb")
    if extra_keep_dup:
        job(3693, "Q-TILE0", "complete",
            {"run": "1", "parent_job_id": 2817, "tile_index": 0, "tile_start": 1, "tile_end": 1656},
            "/data/artifacts/3693/structure.pdb")


@pytest.fixture
def phase_e_db(pre_0014, monkeypatch):
    """⚠ Uses `pre_0014` (index dropped, restored after) so a duplicate CAN be seeded for the negative test."""
    r = _module()
    monkeypatch.setattr(r, "BASELINE_CENSUS", SMALL_BASELINE)
    return pre_0014


def _run(engine, tmp_path, monkeypatch=None):
    r = _module()
    out = tmp_path / "phase_e_read.json"
    rc = r.main(["--url", engine.url.render_as_string(hide_password=False), "--out", str(out)])
    return rc, json.loads(out.read_text(encoding="utf-8"))


def _exp(state):
    return {e["key"]: e for e in state["expectations"]}


@pytest.mark.postgres
def test_baseline_minus_three_passes_end_to_end(phase_e_db, tmp_path):
    """The expected state: collapse done, every other row unchanged. Row-keyed 9 of baseline 12."""
    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3 - 3)
    rc, state = _run(phase_e_db, tmp_path)
    assert rc == 0, [e for e in state["expectations"] if not e["met"]]
    assert state["identity"]["transaction_read_only"] == "on"
    assert state["readings"]["census_row_keyed"] == SMALL_BASELINE - 3
    assert state["readings"]["census_classification"]["verdict"] == "expected"
    assert state["readings"]["census_identity_keyed"] == SMALL_BASELINE - 3
    assert state["readings"]["duplicates"] == {}
    assert all(e["met"] for e in state["expectations"])


@pytest.mark.postgres
def test_the_unchanged_baseline_stops_end_to_end(phase_e_db, tmp_path):
    """⚠ A8.3's named proof: the old 'census untouched' number now FAILS."""
    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3)
    rc, state = _run(phase_e_db, tmp_path)
    assert rc == 2
    assert state["readings"]["census_classification"]["verdict"] == "finding"


@pytest.mark.postgres
def test_one_drop_outside_the_key_is_recorded_and_does_not_stop(phase_e_db, tmp_path):
    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3 - 3 + 1)
    rc, state = _run(phase_e_db, tmp_path)
    assert rc == 0
    v = state["readings"]["census_classification"]
    assert v["verdict"] == "named_category" and v["drops_outside_key"] == 1


@pytest.mark.postgres
def test_a_dropped_row_present_again_stops(phase_e_db, tmp_path):
    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3 - 3 - 1, drop_row_present=True)
    rc, state = _run(phase_e_db, tmp_path)
    assert rc == 2
    assert not _exp(state)["7. drop rows 3693, 3695, 3696 absent from jobs and protein_analyses"]["met"]


@pytest.mark.postgres
def test_a_remaining_duplicate_identity_stops_and_is_named(phase_e_db, tmp_path):
    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3 - 3 - 1, extra_keep_dup=True)
    rc, state = _run(phase_e_db, tmp_path)
    assert rc == 2
    assert not _exp(state)["1. DUPLICATES_SQL returns no row"]["met"]
    assert state["readings"]["identity_groups_with_more_than_one_row"], "the diagnostic did not name the group"


@pytest.mark.postgres
def test_the_read_executes_no_mutation_and_opens_read_only(phase_e_db, tmp_path):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    with phase_e_db.begin() as c:
        _seed(c, complete_whole=SMALL_BASELINE - 3 - 3)
    seen: list[str] = []

    def spy(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        rc, _ = _run(phase_e_db, tmp_path)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    assert rc == 0
    assert any(s.strip() == "SET TRANSACTION READ ONLY" for s in seen)
    assert not [s for s in seen if _MUTATING.search(s)]


from test_d166_collapse_guards import pre_0014  # noqa: E402,F401  (fixture)
