"""D-167 — the re-attach of slice 2's 37: preconditions, plan, capture delivery, and the write.

⚠⚠ Every value the write sets is copied from a measured control or a captured artifact (`D-167` §4).
These tests pin that, and pin that each precondition can FAIL: every mutation below changes ONE fact
about ONE directory (or one global clause) and requires the refusal on exactly that row
(`D-162` rule 7; the `f078_identity_check` pattern).

⚠ RED AT THE ASSERTION, not at an import: the modules under test are resolved through `_module()`,
which asserts they exist before importing them.

⚠ The `@pytest.mark.postgres` half seeds the migrated schema with the 40 rows EXACTLY as
`state_before.json` records them (`jsonb_populate_record`), takes the before-state with the real
Phase B read (`d167_read_state.collect`), and serves structures from a fake surface that resolves
through the database's own `pdb_path` — so the post-write probe is calibrated the way production's is.
"""

from __future__ import annotations

import ast
import base64
import copy
import datetime as dt
import importlib
import importlib.util
import inspect
import json
import re
from pathlib import Path

import pytest
from sqlalchemy import text

import _d167_fixture as fx

REPO = Path(__file__).resolve().parent.parent
REATTACH = REPO / "scripts" / "d167_reattach.py"
CAPTURE = REPO / "scripts" / "d167_volume_capture.py"
NOW = dt.datetime(2026, 9, 16, 16, 0, 0, tzinfo=dt.timezone.utc)


def _module(name: str):
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


def _verify(capture: dict, *, pasted: str | None = None, now: dt.datetime = NOW):
    r = _module("scripts.d167_reattach")
    raw = fx.capture_bytes(capture)
    return r.verify(raw, pasted if pasted is not None else fx.sha(raw),
                    now=now, state_before=fx.load_state_before())


# ── 1. verify(): the good capture passes, and each single mutation fails on its own row ──────────

def test_a_well_formed_capture_is_accepted():
    failures = _verify(fx.synthetic_capture(NOW))
    assert failures == [], failures


def _dirs(cap):
    return cap["dirs"]


def _wrong_sha(cap):
    return cap, "0" * 64


def _stale(cap):
    cap["captured_at"] = (NOW - dt.timedelta(minutes=61)).isoformat()
    return cap, None


def _missing_dir(cap):
    _dirs(cap)["4880"] = {"present": False, "path": "/data/artifacts/4880"}
    return cap, None


def _missing_pae(cap):
    del _dirs(cap)["4890"]["files"]["pae.json.gz"]
    return cap, None


def _size_off_by_one(cap):
    _dirs(cap)["4900"]["files"]["structure.pdb"]["size"] += 1
    return cap, None


def _residue_changed(cap):
    res = _dirs(cap)["4875"]["ca_residues"]
    res[0] = "TRP" if res[0] != "TRP" else "GLY"
    return cap, None


def _folded_at_drift(cap):
    p = _dirs(cap)["4885"]["provenance"]
    t = dt.datetime.fromisoformat(p["folded_at"]) + dt.timedelta(seconds=61)
    p["folded_at"] = t.isoformat()
    return cap, None


def _control_path_format(cap):
    # ⚠ The analysis-id path: the exact mistake D-167 §2 names.
    _dirs(cap)["4867"]["files"]["structure.pdb"]["path"] = "/data/artifacts/4868/structure.pdb"
    return cap, None


def _plddt_array(cap):
    _dirs(cap)["4895"]["plddt"][0] += 5.0
    return cap, None


def _control_plddt_array(cap):
    # ⚠ A3.4: 4867 and 4868 share mean_plddt 58.37. The calibration rows are checked too.
    _dirs(cap)["4867"]["plddt"][0] += 5.0
    return cap, None


@pytest.mark.parametrize("mutate, clause, jobs", [
    (_wrong_sha, "1", None),
    (_stale, "2", None),
    (_missing_dir, "3", {4880}),
    (_missing_pae, "3", {4890}),
    (_size_off_by_one, "5", {4900}),
    (_residue_changed, "6", {4875}),
    (_folded_at_drift, "7", {4885}),
    (_control_path_format, "4", {4867}),
    (_plddt_array, "9", {4895}),
    (_control_plddt_array, "9", {4867}),
], ids=["wrong sha", "stale captured_at", "missing directory", "missing pae.json.gz",
        "size off by one byte", "one CA residue", "folded_at drifted 61 s",
        "control path in the analysis-id format", "plddt.json mean", "control plddt.json mean"])
def test_one_wrong_fact_fails_exactly_its_own_row_and_clause(mutate, clause, jobs):
    good = fx.synthetic_capture(NOW)
    cap, pasted = mutate(copy.deepcopy(good))
    assert fx.capture_bytes(cap) != fx.capture_bytes(good) or pasted, "the mutation changed nothing"
    failures = _verify(cap, pasted=pasted)
    assert failures, "the mutated capture was accepted"
    assert {f.job for f in failures} == ({None} if jobs is None else jobs), failures
    assert any(f.clause.startswith(clause) for f in failures), (clause, failures)


def test_directories_shifted_by_one_fail_identity_on_every_row():
    """⚠⚠ A4.1. The files of job j sitting in directory j+1 pass every size-free, path-format and
    file-set check. Only identity sees it — on all 37, not on some."""
    good = fx.synthetic_capture(NOW)
    cap = copy.deepcopy(good)
    for j in fx.OWED:
        src = copy.deepcopy(good["dirs"][str(fx.LAST if j == fx.FIRST else j - 1)])
        src["path"] = f"{fx.ROOT}/{j}"
        for name, f in src["files"].items():
            f["path"] = f"{fx.ROOT}/{j}/{name}"
            if name == "structure.pdb":
                f["size"] = good["dirs"][str(j)]["files"][name]["size"]
        cap["dirs"][str(j)] = src
    failures = _verify(cap)
    identity = {f.job for f in failures if f.clause.startswith("6")}
    assert identity == set(fx.OWED), sorted(identity ^ set(fx.OWED))


# ── 2. the plan: keyed by job id, copied from the controls, never reading `at` ──────────────────

def _plan(capture=None):
    r = _module("scripts.d167_reattach")
    capture = capture or fx.synthetic_capture(NOW)
    return r.build_plan(capture, fx.load_state_before(), fx.load_progress(),
                        now=NOW, capture_sha="ab" * 32)


def test_the_plan_is_keyed_by_job_id_not_analysis_id():
    """⚠⚠ A4.1 / D-167 §2. Job 4869's analysis is 4870; its structure is in directory 4869."""
    plan = _plan()
    assert [p["job_id"] for p in plan] == list(fx.OWED)
    for p in plan:
        assert p["analysis_id"] == p["job_id"] + 1
        assert p["pdb_path"] == f"/data/artifacts/{p['job_id']}/structure.pdb"
        assert p["pae_json_path"] == f"/data/artifacts/{p['job_id']}/pae.json.gz"


def test_the_plan_copies_the_controls_and_names_what_it_reconstructs():
    plan = _plan()
    for p in plan:
        assert p["structure_source"] == "esmfold", "A3.1: the completion path's own write"
        assert p["tier"] == "local"
        assert p["status_before"] == "pending"
        assert "worker_id" not in p and "claimed_at" not in p, (
            "A3.5: the claim record is preserved NULL, never inferred from the controls")
        md = p["metadata"]
        assert md["fold_provenance"]["folded_at"]
        assert md["reattach"]["decision"] == "D-167"
        assert md["reattach"]["completed_at_reconstructed"] is True
        assert md["reattach"]["capture_sha256"] == "ab" * 32
        assert "sequence" in md, "the existing metadata was replaced rather than merged"


def test_a_missing_pae_leaves_the_column_unwritten():
    """D-106: `pae_json_path` is written only when the file is present."""
    cap = fx.synthetic_capture(NOW)
    del cap["dirs"]["4880"]["files"]["pae.json.gz"]
    plan = {p["job_id"]: p for p in _plan(cap)}
    assert plan[4880]["pae_json_path"] is None
    assert plan[4881]["pae_json_path"] is not None


def test_completed_at_is_folded_at_plus_wall_seconds_on_a_known_control():
    """A1.4 calibration row: job 4866 folded at 15:23:37.539455Z (worker) + 19.17 s."""
    r = _module("scripts.d167_reattach")
    got = r.reconstruct_completed_at("2026-09-13T15:23:37.539455+00:00", "19.17")
    assert got == dt.datetime(2026, 9, 13, 15, 23, 56, 709455, tzinfo=dt.timezone.utc)
    assert got.utcoffset() == dt.timedelta(0)


def test_the_reconstruction_never_reads_the_local_at_column():
    """⚠ `progress.csv`'s `at` is LOCAL (UTC-7). The plan must not need it at all."""
    r = _module("scripts.d167_reattach")
    for fn in (r.reconstruct_completed_at, r.build_plan):
        src = inspect.getsource(fn)
        assert not re.search(r"""\[\s*["']at["']\s*\]|\.get\(\s*["']at["']""", src), fn.__name__
    progress = {j: {k: v for k, v in row.items() if k != "at"} for j, row in fx.load_progress().items()}
    plan = r.build_plan(fx.synthetic_capture(NOW), fx.load_state_before(), progress,
                        now=NOW, capture_sha="ab" * 32)
    assert len(plan) == 37


# ── 3. the capture: delivered byte for byte, standard library only, one write ───────────────────

def test_the_capture_command_payload_is_the_committed_file_byte_for_byte():
    r = _module("scripts.d167_reattach")
    cmd = r.capture_command()
    m = re.search(r"b64decode\('([A-Za-z0-9+/=]+)'\)", cmd)
    assert m, cmd
    assert base64.b64decode(m[1]) == CAPTURE.read_bytes()
    assert cmd.startswith("flyctl ssh console -C ")
    assert "\n" not in cmd and "!" not in cmd


def test_the_capture_imports_only_the_standard_library_and_writes_one_file():
    _module("scripts.d167_volume_capture")
    src = CAPTURE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    allowed = {"__future__", "datetime", "hashlib", "json", "os", "pathlib", "sys"}
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            roots.add((node.module or "").split(".")[0])
    assert roots <= allowed, roots - allowed
    assert ".write_text(" not in src and ".write_bytes(" not in src
    writes = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
              and getattr(n.func, "id", None) == "open"
              and any(isinstance(a, ast.Constant) and "w" in str(a.value) for a in n.args[1:])]
    assert writes, "the capture writes nothing"
    for call in writes:
        assert isinstance(call.args[0], ast.Name) and call.args[0].id == "OUT", ast.dump(call)
    assert 'OUT = "/tmp/d167_capture.json"' in src


def test_the_capture_reads_a_tree_the_way_verify_expects(tmp_path):
    cap = _module("scripts.d167_volume_capture")
    d = tmp_path / "4866"
    d.mkdir()
    (d / "structure.pdb").write_text(
        "ATOM      1  N   MET A   1      0.0   0.0   0.0\n"
        "ATOM      2  CA  MET A   1      0.0   0.0   0.0\n"
        "ATOM      3  CA  GLY A   2      0.0   0.0   0.0\n", encoding="utf-8")
    (d / "plddt.json").write_text("[50.0, 60.0]", encoding="utf-8")
    (d / "provenance.json").write_text('{"mean_plddt": 55.0}', encoding="utf-8")
    out = cap.capture(str(tmp_path), 4866, 4867, NOW)
    got = out["dirs"]["4866"]
    assert got["present"] is True and out["dirs"]["4867"]["present"] is False
    assert got["ca_residues"] == ["MET", "GLY"]
    assert got["plddt"] == [50.0, 60.0] and got["provenance"] == {"mean_plddt": 55.0}
    assert got["files"]["structure.pdb"]["path"] == f"{tmp_path.as_posix()}/4866/structure.pdb"
    assert got["files"]["plddt.json"]["size"] == len(b"[50.0, 60.0]")
    assert out["captured_at"] == NOW.isoformat()


# ── 4. the guard enumeration sees the new writer (C.2.7) ────────────────────────────────────────

def test_the_reattach_is_an_enumerated_owner_gated_writer_with_no_exception():
    _module("scripts.d167_reattach")
    from test_d159_enqueue_identity import IDENTITY_CHECK_EXCEPTIONS, owner_gated_writers

    assert "scripts/d167_reattach.py" in owner_gated_writers(), (
        "not enumerated - is the file git-added (D-162 rule 6)?")
    assert "scripts/d167_reattach.py" not in IDENTITY_CHECK_EXCEPTIONS


def test_the_dry_run_reads_through_the_read_only_helper():
    r = _module("scripts.d167_reattach")
    src = inspect.getsource(r.main)
    assert "read_only_transaction(eng)" in src, "the dry run is not read-only by the database"


# ── 5. postgres: the write, end to end ──────────────────────────────────────────────────────────

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b", re.I)


@pytest.fixture
def seeded(pg_engine, tmp_path):
    """Marker + floor, then the 40 rows exactly as `state_before.json` records them; the before-state
    is re-taken from THIS database by the real Phase B read and written to tmp."""
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from scripts.d167_read_state import collect, read_only_transaction, write_state
    from test_d166_collapse_guards import _seed_population

    real = fx.load_state_before()
    with pg_engine.begin() as c:
        c.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
        c.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"),
                  {"c": LIVE_CLUSTER_ID})
        _seed_population(c, CENSUS_FLOOR)
        for row in real["control"] + real["owed_37"]:
            c.execute(text("INSERT INTO protein_analyses SELECT * FROM "
                           "jsonb_populate_record(NULL::protein_analyses, CAST(:r AS jsonb))"),
                      {"r": json.dumps(row["analysis"])})
            c.execute(text("INSERT INTO jobs SELECT * FROM "
                           "jsonb_populate_record(NULL::jobs, CAST(:r AS jsonb))"),
                      {"r": json.dumps(row["job"])})
    with read_only_transaction(pg_engine) as conn:
        write_state(collect(conn), tmp_path / "state_before.json")
    try:
        yield pg_engine
    finally:
        with pg_engine.begin() as c:
            c.execute(text(f"DROP TABLE IF EXISTS {LIVE_MARKER_TABLE}"))
            c.execute(text(
                "TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE"))


def _fetch_from(engine):
    """A serving surface that resolves through the database's own `pdb_path`, like production's."""
    def fetch(url: str):
        m = re.search(r"/api/analyses/(\d+)(/structure)?$", url)
        assert m, url
        with engine.connect() as c:
            row = c.execute(text(
                "SELECT j.id AS job_id, a.pdb_path, a.metadata FROM protein_analyses a "
                "JOIN jobs j ON j.analysis_id = a.id WHERE a.id = :a"), {"a": int(m[1])}).first()
        if row is None:
            return 404, b""
        if m[2]:
            return (404, b"") if row.pdb_path is None else (200, fx.structure_body(row.job_id))
        return 200, json.dumps({"fold_provenance": (row.metadata or {}).get("fold_provenance")}).encode()
    return fetch


def _run(engine, tmp_path, *extra, capture=None):
    r = _module("scripts.d167_reattach")
    cap = capture or fx.synthetic_capture(dt.datetime.now(dt.timezone.utc))
    raw = fx.capture_bytes(cap)
    path = tmp_path / "capture.json"
    path.write_bytes(raw)
    url = engine.url.render_as_string(hide_password=False)
    return r.main(["--url", url, "--capture", str(path), "--capture-sha", fx.sha(raw),
                   "--state-before", str(tmp_path / "state_before.json"), *extra],
                  fetch=_fetch_from(engine))


def _owed_state(engine):
    with engine.connect() as c:
        return c.execute(text(
            "SELECT count(*) FILTER (WHERE j.status = 'complete'), count(a.pdb_path), "
            "count(*) FILTER (WHERE a.structure_source = 'esmfold'), "
            "count(*) FILTER (WHERE j.tier = 'local') "
            "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
            "WHERE j.id BETWEEN 4869 AND 4905")).one()


@pytest.mark.postgres
def test_the_owner_run_writes_exactly_37_and_37_as_designed(seeded, tmp_path):
    rc = _run(seeded, tmp_path, "--i-am-the-owner")
    assert rc == 0
    assert tuple(_owed_state(seeded)) == (37, 37, 37, 37)
    progress = fx.load_progress()
    with seeded.connect() as c:
        rows = c.execute(text(
            "SELECT j.id, j.completed_at, j.worker_id, j.claimed_at, j.attempts, a.metadata "
            "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
            "WHERE j.id BETWEEN 4869 AND 4905 ORDER BY j.id")).all()
    for row in rows:
        prov = row.metadata["fold_provenance"]
        want = (dt.datetime.fromisoformat(prov["folded_at"])
                + dt.timedelta(seconds=float(progress[row.id]["wall_seconds"])))
        assert row.completed_at == want
        assert row.worker_id is None and row.claimed_at is None and row.attempts == 0
        assert row.metadata["reattach"]["decision"] == "D-167"


@pytest.mark.postgres
def test_after_the_write_the_apps_own_completion_invariant_holds(seeded, tmp_path):
    """C.2.6: `artifacts_present` is the invariant `/complete` itself enforces."""
    from app.artifacts import artifacts_present

    assert _run(seeded, tmp_path, "--i-am-the-owner") == 0
    assert all(artifacts_present(seeded, j) for j in fx.OWED)


@pytest.mark.postgres
def test_a_second_run_refuses_rather_than_silently_doing_nothing(seeded, tmp_path):
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 0
    after = tuple(_owed_state(seeded))
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 1
    assert tuple(_owed_state(seeded)) == after


@pytest.mark.postgres
def test_a_row_that_moved_since_the_read_refuses_the_whole_transaction(seeded, tmp_path):
    with seeded.begin() as c:
        c.execute(text("UPDATE jobs SET attempts = 1 WHERE id = 4880"))
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 1
    assert tuple(_owed_state(seeded)) == (0, 0, 0, 0)


@pytest.mark.postgres
def test_a_claimed_job_refuses(seeded, tmp_path):
    with seeded.begin() as c:
        aid = c.execute(text("INSERT INTO protein_analyses (input_type, input_value, metadata) "
                             "VALUES ('uniprot', 'P-LIVE', '{}') RETURNING id")).scalar_one()
        c.execute(text("INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
                       "VALUES (9001, :a, 'claimed', 1, '{}')"), {"a": aid})
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 1
    assert tuple(_owed_state(seeded)) == (0, 0, 0, 0)


@pytest.mark.postgres
def test_no_marker_refuses(seeded, tmp_path):
    from core.db_identity import LIVE_MARKER_TABLE

    with seeded.begin() as c:
        c.execute(text(f"DROP TABLE {LIVE_MARKER_TABLE}"))
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 1
    assert tuple(_owed_state(seeded)) == (0, 0, 0, 0)


@pytest.mark.postgres
def test_a_sibling_population_other_than_esmfold_refuses(seeded, tmp_path):
    """⚠ A3.1: three controls are not the population. One more complete sibling in slice 2's range
    carrying another source moves the grouped count away from the before-state."""
    with seeded.begin() as c:
        aid = c.execute(text(
            "INSERT INTO protein_analyses (input_type, input_value, metadata, pdb_path, "
            "structure_source) VALUES ('uniprot', 'P-SIB', '{}', '/data/artifacts/4500/structure.pdb', "
            "'esmfold_local') RETURNING id")).scalar_one()
        c.execute(text("INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
                       "VALUES (4500, :a, 'complete', 1, '{}')"), {"a": aid})
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 1
    assert tuple(_owed_state(seeded)) == (0, 0, 0, 0)


@pytest.mark.postgres
def test_the_dry_run_executes_no_mutation_and_is_read_only_first(seeded, tmp_path):
    """C.2.8: without `--i-am-the-owner`, zero mutating statements reach the database."""
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    seen: list[str] = []

    def spy(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        rc = _run(seeded, tmp_path)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    assert rc == 0
    assert any(s.strip() == "SET TRANSACTION READ ONLY" for s in seen)
    hits = [s for s in seen if _MUTATING.search(s)]
    assert not hits, hits
    assert tuple(_owed_state(seeded)) == (0, 0, 0, 0)


@pytest.mark.postgres
def test_revert_restores_the_before_state_exactly(seeded, tmp_path):
    from scripts.d167_read_state import collect, read_only_transaction

    assert _run(seeded, tmp_path, "--i-am-the-owner") == 0
    r = _module("scripts.d167_reattach")
    url = seeded.url.render_as_string(hide_password=False)
    assert r.main(["--url", url, "--revert", "--i-am-the-owner",
                   "--state-before", str(tmp_path / "state_before.json")]) == 0
    before = json.loads((tmp_path / "state_before.json").read_text(encoding="utf-8"))
    with read_only_transaction(seeded) as conn:
        now = collect(conn)
    assert now["owed_37"] == before["owed_37"]
    assert now["control"] == before["control"]


@pytest.mark.postgres
def test_the_witness_reads_the_before_value_and_the_after_value(seeded, tmp_path, capsys):
    """F-080: the before-value is what makes it a witness. Seeded, slice 2's range holds the 3
    controls before and 40 after."""
    r = _module("scripts.d167_reattach")
    url = seeded.url.render_as_string(hide_password=False)
    assert r.main(["--url", url, "--witness"]) == 0
    assert re.search(r"^witness: 3$", capsys.readouterr().out, re.M)
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 0
    capsys.readouterr()
    assert r.main(["--url", url, "--witness"]) == 0
    assert re.search(r"^witness: 40$", capsys.readouterr().out, re.M)


@pytest.mark.postgres
def test_the_reattach_proceeds_when_the_role_cannot_build_the_index(seeded, tmp_path, monkeypatch,
                                                                     capsys):
    """⚠ A4.2: the re-attach depends on neither the collapse nor `0014`. It reports and proceeds."""
    r = _module("scripts.d167_reattach")
    monkeypatch.setattr(r, "role_preamble", lambda conn: {
        "session_user": "x", "current_user": "x", "role": "none", "rolconfig": None,
        "rolsuper": False, "jobs_owner": "someone_else", "can_build_jobs_index": False})
    assert _run(seeded, tmp_path, "--i-am-the-owner") == 0
    assert "someone_else" in capsys.readouterr().out
