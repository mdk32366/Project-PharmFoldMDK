"""D-167 step 1 — the read is read-only BY THE DATABASE, asks identity first, and keeps its evidence.

⚠⚠ `ORDERS-Code-2026-09-16` A1.8: ad-hoc SQL pasted into a tunnel shell is state outside version
control that determines a result (`D-162` rule 8), and it is read-only by intention. So the read is a
committed script, and these tests pin the three properties that make it safe to hand to the owner:

1. **Nothing it executes mutates** — checked over its own code AND the collapse helpers it imports.
2. **The transaction is read-only at the database** — `SET TRANSACTION READ ONLY` first, and
   calibrated on real Postgres: an `UPDATE` inside the helper raises, and the same `UPDATE` without
   the helper does not (rule 7: say what the probe returns when the thing is absent).
3. **`D-159` before any reported read**, and the output is written once, with its sha256.
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import re
from pathlib import Path

import pytest
from sqlalchemy import text

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "d167_read_state.py"

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bALTER\s+TABLE\b|\bCREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX|SCHEMA|EXTENSION)\b"
    r"|\bDROP\s+(?:TABLE|INDEX|SCHEMA)\b", re.I)


# ── 1. nothing it executes mutates ──────────────────────────────────────────────────────────────

def test_the_sql_the_read_executes_contains_no_mutation():
    """⚠ Over the read's own code (docstrings and comments blanked — `test_d159`'s `_code_only`,
    one home) AND the SQL it borrows from the collapse, because an imported query is executed here
    too."""
    from test_d159_enqueue_identity import _code_only

    import scripts.d166_collapse_duplicate_tiles as collapse

    own = _code_only(SCRIPT.read_text(encoding="utf-8"))
    borrowed = "\n".join([
        str(collapse.DUPLICATES_SQL), str(collapse.CLAIMED_SQL), str(collapse.FOREIGN_KEYS_SQL),
        inspect.getsource(collapse.foreign_keys), inspect.getsource(collapse.referencing_rows)])
    for label, body in (("scripts/d167_read_state.py", own), ("collapse helpers", borrowed)):
        hit = _MUTATING.search(body)
        assert hit is None, f"{label} executes a mutation: {hit.group(0)!r}"


def test_the_mutation_detector_can_fail():
    """`F-045`: shown to bite on the shapes it claims to catch."""
    for bad in ("UPDATE jobs SET tier = 'local'", "delete from jobs", "CREATE UNIQUE INDEX x ON y",
                "DROP TABLE keel_live_cluster", "TRUNCATE jobs"):
        assert _MUTATING.search(bad), bad
    assert _MUTATING.search("SELECT count(*) FROM jobs WHERE status = 'complete'") is None


# ── 2. read-only at the database ────────────────────────────────────────────────────────────────

class _RecordingConn:
    def __init__(self, marker=None, rows=0, anchor=False):
        self.marker, self.rows, self.anchor = marker, rows, anchor
        self.statements: list[str] = []

    def execute(self, stmt, params=None):
        sql = str(stmt)
        self.statements.append(sql)
        value = (self.marker if "to_regclass" in sql and self.marker else
                 None if "to_regclass" in sql else
                 self.marker if "cluster_id" in sql else
                 self.rows if "count(*)" in sql else
                 (1 if self.anchor else None))
        return _Scalar(value)


class _Scalar:
    def __init__(self, v):
        self._v = v

    def scalar(self):
        return self._v


class _FakeEngine:
    def __init__(self):
        self.conn = _RecordingConn()

    @contextlib.contextmanager
    def begin(self):
        yield self.conn


def test_the_transaction_helper_sets_read_only_as_its_first_statement():
    from scripts.d167_read_state import read_only_transaction

    eng = _FakeEngine()
    with read_only_transaction(eng) as conn:
        conn.execute(text("SELECT 1"))
    assert eng.conn.statements[0] == "SET TRANSACTION READ ONLY", eng.conn.statements
    assert eng.conn.statements[1] == "SELECT 1"


def test_main_reads_only_through_the_helper():
    """⚠ The helper is worthless if `main` opens a transaction around it. One `with` in `main`, and
    it is the helper's."""
    src = inspect.getsource(__import__("scripts.d167_read_state", fromlist=["main"]).main)
    assert "read_only_transaction(eng)" in src
    assert "eng.begin()" not in src and "eng.connect()" not in src


@pytest.mark.postgres
def test_postgres_refuses_a_write_inside_the_helper_and_not_outside_it(pg_engine):
    """⚠⚠ The calibration. Inside the helper an UPDATE raises `read-only transaction`; the same
    UPDATE in an ordinary transaction does not — so the refusal is the helper's doing, not an
    accident of the fixture's permissions."""
    from scripts.d167_read_state import read_only_transaction

    probe = text("UPDATE jobs SET attempts = attempts")
    with pytest.raises(Exception) as exc:
        with read_only_transaction(pg_engine) as conn:
            conn.execute(probe)
    assert "read-only transaction" in str(exc.value), str(exc.value)

    with pg_engine.begin() as conn:          # negative control: permitted without the helper
        conn.execute(probe)


# ── 3. identity first, evidence kept ────────────────────────────────────────────────────────────

def test_identity_is_asked_before_any_reported_read():
    """A target with no marker is refused having asked only the identity probes."""
    from core.db_identity import WrongDatabase
    from scripts.d167_read_state import collect

    conn = _RecordingConn(marker=None, rows=99999, anchor=True)
    with pytest.raises(WrongDatabase):
        collect(conn)
    reported = [s for s in conn.statements
                if re.search(r"to_jsonb|information_schema|FROM jobs|alembic_version", s)]
    assert not reported, f"read before the identity check refused: {reported}"
    assert conn.statements, "the identity check asked nothing"


def test_the_state_is_written_once_with_its_sha256(tmp_path):
    from scripts.d167_read_state import OUT, write_state

    assert OUT == REPO / "data" / "control" / "d167" / "state_before.json"
    target = tmp_path / "d167" / "state_before.json"
    sha = write_state({"b": 2, "a": [1]}, target)
    assert sha == hashlib.sha256(target.read_bytes()).hexdigest()
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": [1], "b": 2}
    with pytest.raises(SystemExit):
        write_state({"c": 3}, target)            # evidence is not overwritten by a later read
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": [1], "b": 2}


def test_task3_overlap_is_computed_from_the_rows_given():
    """⚠ `ORDERS` A2.2: key 3 (`run = 2` + span 1-30) also counts Task 3's Run-2 rows in that band,
    which slice 2's enqueue excluded. The overlap is computed from the committed file IN THE RUN —
    never a hard-coded 8 — so a synthetic file must give a synthetic answer."""
    import scripts.d167_read_state as r

    fn = getattr(r, "task3_overlap_ids", None)
    assert fn is not None, "the read has no task3_overlap_ids: the Task 3 overlap is not computed"
    rows = [{"job_id": 11, "span_aa": 1}, {"job_id": 12, "span_aa": 30}, {"job_id": 13, "span_aa": 31},
            {"job_id": 10, "span_aa": 0}, {"job_id": 14, "span_aa": "27"}]
    assert fn(rows, (1, 30)) == [11, 12, 14]
    assert fn([], (1, 30)) == []


def test_the_task3_file_the_overlap_reads_is_the_committed_one():
    import scripts.d167_read_state as r

    path = getattr(r, "TASK3_ENQUEUED_JSON", None)
    assert path == REPO / "data" / "control" / "task3_run2" / "enqueued.json"
    assert path.is_file()


def test_main_prints_the_sha256_and_records_the_commit():
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'print(f"sha256  : {sha}")' in src
    assert '"commit": _git("rev-parse", "HEAD")' in src


# ── the read, end to end, on a seeded migrated database ─────────────────────────────────────────

@pytest.fixture
def seeded(pg_engine):
    """Marker + floor, then jobs 4866-4905 with analysis_id = job id + 1: three complete controls and
    37 NULL-tier pending rows with no path — the state the pre-work records."""
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from test_d166_collapse_guards import _seed_population

    with pg_engine.begin() as c:
        c.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
        c.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"),
                  {"c": LIVE_CLUSTER_ID})
        _seed_population(c, CENSUS_FLOOR)
        for job_id in range(4866, 4906):
            control = job_id <= 4868
            c.execute(text(
                "INSERT INTO protein_analyses (id, input_type, input_value, metadata, pdb_path) "
                "VALUES (:a, 'uniprot', :v, CAST(:m AS jsonb), :p)"),
                {"a": job_id + 1, "v": f"Q{job_id}", "m": '{"span_aa": 29}',
                 "p": f"/data/artifacts/{job_id}/structure.pdb" if control else None})
            c.execute(text(
                "INSERT INTO jobs (id, analysis_id, status, attempts, tier, inference_settings) "
                "VALUES (:j, :a, :s, :n, :t, CAST(:i AS jsonb))"),
                {"j": job_id, "a": job_id + 1, "s": "complete" if control else "pending",
                 "n": 1 if control else 0, "t": "local" if control else None, "i": '{"run": 2}'})
    try:
        yield pg_engine
    finally:
        with pg_engine.begin() as c:
            c.execute(text(f"DROP TABLE IF EXISTS {LIVE_MARKER_TABLE}"))
            c.execute(text(
                "TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE"))


@pytest.mark.postgres
def test_the_read_measures_the_seeded_state(seeded, tmp_path):
    """The read reports what is there. ⚠ It exits 2 here BY DESIGN: CI's chain is at `0014` and
    seeds no duplicates and 3 folded slice-2 rows, so those expectations are NOT MET — which is the
    proof that "not met" is reported rather than smoothed."""
    from scripts.d167_read_state import main

    out = tmp_path / "state_before.json"
    rc = main(["--url", seeded.url.render_as_string(hide_password=False), "--out", str(out)])
    state = json.loads(out.read_text(encoding="utf-8"))
    exp = {e["key"]: e for e in state["expectations"]}

    assert rc == 2
    assert state["identity"]["transaction_read_only"] == "on"
    assert len(state["owed_37"]) == 37 and len(state["control"]) == 3
    assert "tier" in state["columns"]["jobs"] and "metadata" in state["columns"]["protein_analyses"]
    for key in ("3. analysis_id - job_id over jobs 4866-4905 (distinct values)",
                "4. jobs rows, id 4869-4905", "4. of those, status = 'complete'",
                "4. of those, analysis pdb_path IS NOT NULL", "4. of those, tier IS NULL",
                "4. control 4866-4868, status = 'complete' AND pdb_path IS NOT NULL",
                KEYS_1_2_AGREE, KEY3_MINUS_KEY2,
                "7. rows outside the collapse referencing its drop rows",
                JSON_PARENT_REFS,
                "8. jobs with status = 'claimed'"):
        assert exp[key]["met"], (key, exp[key])
    assert not exp["9. alembic_version"]["met"]
    assert not exp["6. DUPLICATES_SQL"]["met"]
    assert {v["complete_and_pdb_path"] for v in state["slice2"].values()} == {3}
    assert state["task3_overlap"]["ids_complete_in_db"] == []


#: ⚠ The expectation keys A2.2 introduces, named once so the two end-to-end tests cannot drift apart.
KEYS_1_2_AGREE = "5. keys 1 and 2 agree (id range, enqueued.json)"
KEY3_MINUS_KEY2 = ("5. key 3 minus key 2 equals task3_overlap "
                   "(Task 3 Run-2 rows in band 1-30, complete with pdb_path)")
JSON_PARENT_REFS = ("7. jobs naming a drop row as inference_settings parent_job_id "
                    "(no declared constraint)")


@pytest.mark.postgres
def test_a_task3_row_in_band_is_a_named_category_not_a_disagreement(seeded, tmp_path):
    """⚠⚠ A2.2. One Task 3 Run-2 row in band 1-30, complete with a path — job 3698, span 1, exactly
    as `data/control/task3_run2/enqueued.json` lists it. Key 3 now exceeds keys 1-2 by one.

    ⚠ The OLD expectation ("the three keys agree") FAILS on this state — shown below from the measured
    counts — and the NEW one passes, because the difference is the overlap the committed file
    predicts rather than an unexplained disagreement."""
    from scripts.d167_read_state import main

    with seeded.begin() as c:
        c.execute(text(
            "INSERT INTO protein_analyses (id, input_type, input_value, metadata, pdb_path) "
            "VALUES (103698, 'uniprot', 'Q-T3', CAST('{\"span_aa\": 1}' AS jsonb), "
            "'/data/artifacts/3698/structure.pdb')"))
        c.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, tier, inference_settings) "
            "VALUES (3698, 103698, 'complete', 1, 'local', CAST('{\"run\": 2}' AS jsonb))"))

    out = tmp_path / "state_before.json"
    main(["--url", seeded.url.render_as_string(hide_password=False), "--out", str(out)])
    state = json.loads(out.read_text(encoding="utf-8"))
    exp = {e["key"]: e for e in state["expectations"]}
    counts = [v["complete_and_pdb_path"] for v in state["slice2"].values()]

    assert len(set(counts)) != 1, f"the old three-key agreement would NOT fail here: {counts}"
    assert exp[KEYS_1_2_AGREE]["met"], exp[KEYS_1_2_AGREE]
    assert exp[KEY3_MINUS_KEY2]["met"], exp[KEY3_MINUS_KEY2]
    assert exp[KEY3_MINUS_KEY2]["measured"] == 1
    assert state["task3_overlap"]["ids_complete_in_db"] == [3698]
    assert len(state["task3_overlap"]["ids_in_band"]) >= 1
