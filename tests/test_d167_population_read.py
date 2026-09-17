"""R1-R4, the population-aware read (ORDERS-Code-2026-09-17-R1-R4; A9.2 carried verbatim) -- tests first.

⚠⚠ Why this exists. The Phase E read (`d167_phase_e_read.py`) stopped on expectation 3: identity-keyed
3,576 against row-keyed 3,648. The 72 were explained from committed files as the cohort-82 x census overlap
(one protein folded once per population), but the un-truncated group list and each row's `cohort_tranche`
were NEVER READ. R1-R4 read them:

    R1  groups of (accession, tile_start, tile_end) with > 1 complete run '1' row, its own count(*)   72
    R2  each such group holds exactly one cohort_tranche = 0 row and exactly one tranche >= 1 row  72 of 72
    R3  the identity key WITH population: groups with > 1 complete row                               0
    R4  P11717, Q8WXI7, Q9NYQ8: no complete tranche-0 row and exactly one complete census row       3 of 3

⚠⚠ The defect class this instrument must not repeat: a count derived from the length of a list. The
Phase E diagnostic ran `LIMIT 50` and printed "50" as a count. So every reading here is its own
`count(*)`, every printed list says whether it is capped, and a postgres test caps the list BELOW the
true count and proves the reading does not move.

⚠⚠ A-017: every assertion is shown capable of failing. Each of R1, R2, R3 and R4 has a fixture that
misses it, and an empty database fails.

⚠ RED AT THE ASSERTION: the module under test is resolved through `_module()`, which asserts it exists.
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
SCRIPT = REPO / "scripts" / "d167_population_read.py"

_MUTATING = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bALTER\s+TABLE\b|\bCREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX|SCHEMA|EXTENSION)\b"
    r"|\bDROP\s+(?:TABLE|INDEX|SCHEMA)\b", re.I)


def _module():
    name = "scripts.d167_population_read"
    assert importlib.util.find_spec(name) is not None, f"{name} does not exist"
    return importlib.import_module(name)


# -- 1. the pre-registered expectations, exactly as A9.2 states them -----------------------------

def test_the_expectations_are_the_pre_registered_values():
    r = _module()
    assert r.EXPECTED_R1 == 72
    assert r.EXPECTED_R3 == 0
    assert r.R4_ACCESSIONS == ("P11717", "Q8WXI7", "Q9NYQ8")
    assert r.EXPECTED_R4 == 3


def test_the_output_is_its_own_evidence_file_never_the_phase_e_one():
    r = _module()
    assert r.OUT == REPO / "data" / "control" / "d167" / "population_read" / "r1r4_read.json"


def test_the_population_convention_is_the_source_one_and_null_is_its_own_category():
    """Tranche 0 is the cohort (`scripts/census_ingest.py` COHORT_TRANCHE; migration 0008's backfill);
    >= 1 is census; NULL is UNCLASSIFIED (`db/models.py`) and must never be folded into either."""
    r = _module()
    sql = " ".join(r.POPULATION_SQL.split())
    assert "a.cohort_tranche = 0 THEN 'cohort'" in sql
    assert "a.cohort_tranche >= 1 THEN 'census'" in sql
    assert "ELSE 'untagged'" in sql


# -- 2. the defect class: a count is never the length of a list ----------------------------------

def test_collect_derives_no_count_from_a_list_length():
    """⚠⚠ The Phase E defect. `len(` anywhere in `collect` is a count taken from a list."""
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.collect))
    assert "len(" not in code, "collect() takes a length; every reading must be its own count(*)"


def test_every_reading_query_is_a_count():
    r = _module()
    for name in ("R1_SQL", "R2_SQL", "R3_SQL", "R4_SQL", "UNTAGGED_SQL", "R1_SIZES_SQL",
                 "RUN_LABEL_SQL", "TRANCHE0_RUN_LABEL_SQL"):
        sql = getattr(r, name)
        assert "count(*)" in sql, f"{name} is not a count(*)"
        assert "LIMIT" not in sql.upper(), f"{name} is capped; a capped query is never a count"


def test_a_capped_list_is_labelled_capped_and_never_printed_as_a_count():
    r = _module()
    d = r.capped_list("R1 groups", count=72, rows=[{"a": i} for i in range(50)], cap=50)
    assert d["capped"] is True and d["count"] == 72 and d["rows_shown"] == 50
    line = r.format_capped(d)
    assert "CAPPED" in line and "72" in line
    assert not re.search(r"\b50\b(?! shown)", line.replace("cap 50", "")), \
        f"the list length is printed as if it were a count: {line!r}"


def test_an_uncapped_list_says_it_is_complete():
    r = _module()
    d = r.capped_list("R3 groups", count=0, rows=[], cap=100)
    assert d["capped"] is False
    line = r.format_capped(d)
    assert "CAPPED" not in line and "complete" in line


def test_a_list_shorter_than_its_count_is_capped_even_below_the_cap():
    """A mismatch between the count and the rows is never presented as complete."""
    r = _module()
    assert r.capped_list("x", count=3, rows=[{}, {}], cap=100)["capped"] is True


# -- 3. read-only, role first, identity second, evidence kept, ASCII ------------------------------

def test_the_script_executes_no_mutation():
    from test_d159_enqueue_identity import _code_only

    _module()
    hit = _MUTATING.search(_code_only(SCRIPT.read_text(encoding="utf-8")))
    assert hit is None, f"the population read executes a mutation: {hit.group(0)!r}"


def test_main_reads_only_through_the_read_only_helper():
    r = _module()
    src = inspect.getsource(r.main)
    assert "read_only_transaction(eng)" in src
    assert "eng.begin()" not in src and "eng.connect()" not in src


def test_role_then_identity_then_the_first_read():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.collect))
    role, ident = code.index("role_preamble(conn)"), code.index("assert_campaign_target(conn)")
    first_read = code.index("R1_SQL")
    assert role < ident < first_read


def test_the_output_is_written_once_with_its_sha256():
    src = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
    _module()
    assert "write_state(" in src, "the write-once helper is not reused (one home: d167_read_state)"
    assert 'print(f"sha256  : {sha}")' in src


def test_the_run_label_predicate_is_stated_and_its_outside_is_measured():
    """⚠ Owner ruling 2026-09-17 section 5 owes this. `run` is a JSON INTEGER (backfill_run_label.py
    RUN_1 = 1, census_ingest.py, task3 RUN_LABEL = 2) read as text through `->>`. An ABSENT label is not
    Run 1 (F-018), and `core/hold48.py` emits tile jobs with no run key at all -- so the two run-label
    diagnostics measure what falls outside the key instead of assuming nothing does."""
    r = _module()
    assert "->>'run' = '1'" in r.R1_SQL
    for sql in (r.RUN_LABEL_SQL, r.TRANCHE0_RUN_LABEL_SQL):
        assert "coalesce(j.inference_settings->>'run', '(absent)')" in sql
        assert "->>'run' = '1'" not in sql, "a diagnostic of what is outside the key cannot apply the key"
    assert "a.cohort_tranche = 0" in r.TRANCHE0_RUN_LABEL_SQL


def test_a_non_ascii_printed_line_is_escaped_not_dropped():
    """⚠ The shared `core.db_role.format_preamble` header carries a section sign. CI caught it in the
    printed output of the first push; the source-only ASCII test could not."""
    r = _module()
    line = r.ascii_line("ROLE PREAMBLE (D-167 amendment 1 §2, read-only)")
    assert all(ord(ch) < 128 for ch in line)
    assert "\\xa72" in line


def test_main_prints_nothing_except_through_the_ascii_helper():
    from test_d159_enqueue_identity import _code_only

    r = _module()
    code = _code_only(inspect.getsource(r.main))
    bare = [ln.strip() for ln in code.splitlines() if ln.strip().startswith("print(")]
    assert bare == ['print(f"sha256  : {sha}")'], f"printing around the ASCII helper: {bare}"


def test_the_script_source_is_ascii():
    """⚠ A7.4: a PowerShell pipe under cp1252 cannot turn ASCII evidence into a traceback."""
    from test_d159_enqueue_identity import _code_only

    _module()
    code = _code_only(SCRIPT.read_text(encoding="utf-8"))
    bad = sorted({ch for ch in code if ord(ch) > 127})
    assert not bad, f"non-ASCII characters in executable code: {bad}"


# -- 4. postgres: every reading shown capable of failing -----------------------------------------

SMALL_R1 = 2      # the clean fixture holds two cohort x census pairs


def _seed(conn, *, pairs: int = 2, same_population_dup: bool = False, untagged_partner: bool = False,
          drop_fat2_census: bool = False, empty: bool = False, unlabelled_tile: bool = False):
    """Marker + D-159 floor, then a miniature of production:

    - `pairs` accessions folded once per population (tranche 0 + tranche 1), both complete run '1'
    - a census-only row (tranche 2), a run '2' row on a paired accession (must not count)
    - MUC16 Q8WXI7: tranche-0 pending; census parent complete + two complete tiles (tranche 5)
    - IGF2R P11717: tranche-0 failed; census complete (tranche 5)
    - FAT2 Q9NYQ8: tranche-0 pending; census complete (tranche 5)
    """
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE
    from test_d166_collapse_guards import _seed_population

    conn.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
    conn.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"), {"c": LIVE_CLUSTER_ID})
    _seed_population(conn, CENSUS_FLOOR)
    if empty:
        return

    def job(job_id, acc, tranche, status, settings):
        pdb = f"/data/artifacts/{job_id}/structure.pdb" if status == "complete" else None
        conn.execute(text(
            "INSERT INTO protein_analyses (id, input_type, input_value, cohort_tranche, metadata, pdb_path) "
            "VALUES (:a, 'uniprot', :v, :t, '{}', :p)"), {"a": job_id, "v": acc, "t": tranche, "p": pdb})
        conn.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (:j, :a, :s, 1, CAST(:i AS jsonb))"),
            {"j": job_id, "a": job_id, "s": status, "i": json.dumps(settings)})

    whole = {"run": "1", "ecd_start": 1, "ecd_end": 30}
    for n in range(pairs):
        acc = f"O9{n:04d}"
        job(900000 + n, acc, 0, "complete", whole)
        partner_tranche = None if (untagged_partner and n == pairs - 1) else 1
        job(910000 + n, acc, partner_tranche, "complete", whole)
    if same_population_dup:
        job(920000, "O90000", 3, "complete", whole)
    job(930000, "P95001", 2, "complete", whole)
    job(940000, "O90000", 1, "complete", {**whole, "run": "2"})

    job(950000, "Q8WXI7", 0, "pending", whole)
    job(950001, "Q8WXI7", 5, "complete", whole)
    for k, (s, e) in enumerate(((1, 1656), (1609, 3264))):
        job(950010 + k, "Q8WXI7", 5, "complete",
            {"run": "1", "parent_job_id": 950001, "tile_index": k, "tile_start": s, "tile_end": e})
    if unlabelled_tile:
        # ⚠ core/hold48.py emits tile jobs with NO run key: outside the run-'1' key entirely.
        job(950020, "Q8WXI7", 5, "complete",
            {"parent_job_id": 950001, "tile_index": 9, "tile_start": 3217, "tile_end": 4872})
    job(960000, "P11717", 0, "failed", whole)
    job(960001, "P11717", 5, "complete", whole)
    job(970000, "Q9NYQ8", 0, "pending", whole)
    if not drop_fat2_census:
        job(970001, "Q9NYQ8", 5, "complete", whole)


@pytest.fixture
def pop_db(pre_0014, monkeypatch):
    r = _module()
    monkeypatch.setattr(r, "EXPECTED_R1", SMALL_R1)
    return pre_0014


def _run(engine, tmp_path, capsys=None):
    r = _module()
    out = tmp_path / "r1r4_read.json"
    rc = r.main(["--url", engine.url.render_as_string(hide_password=False), "--out", str(out)])
    printed = capsys.readouterr().out if capsys is not None else ""
    return rc, json.loads(out.read_text(encoding="utf-8")), out.read_bytes(), printed


def _met(state):
    return {e["key"].split(" ")[0]: e["met"] for e in state["expectations"]}


@pytest.mark.postgres
def test_the_clean_population_meets_all_four(pop_db, tmp_path, capsys):
    with pop_db.begin() as c:
        _seed(c)
    rc, state, body, printed = _run(pop_db, tmp_path, capsys)
    assert rc == 0, [e for e in state["expectations"] if not e["met"]]
    assert state["identity"]["transaction_read_only"] == "on"
    rd = state["readings"]
    assert rd["R1"] == SMALL_R1
    assert rd["R2"] == {"meeting": SMALL_R1, "of": SMALL_R1}
    assert rd["R3"] == 0
    assert rd["R4"] == 3
    assert _met(state) == {"R1": True, "R2": True, "R3": True, "R4": True}
    assert all(b < 128 for b in body), "non-ASCII byte in the evidence file"
    assert all(ord(ch) < 128 for ch in printed), "non-ASCII character in the printed output"


@pytest.mark.postgres
def test_R3_fails_on_a_same_population_duplicate(pop_db, tmp_path):
    """⚠⚠ The orders' named discriminating fixture: a second census row at one identity."""
    with pop_db.begin() as c:
        _seed(c, same_population_dup=True)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 2
    assert state["readings"]["R3"] == 1
    assert _met(state)["R3"] is False
    assert state["diagnostics"]["R3_groups"]["count"] == 1


@pytest.mark.postgres
def test_R1_fails_when_the_group_count_moves(pop_db, tmp_path):
    with pop_db.begin() as c:
        _seed(c, pairs=1)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 2
    assert state["readings"]["R1"] == 1
    assert _met(state)["R1"] is False


@pytest.mark.postgres
def test_R2_fails_when_a_partner_is_untagged_and_R3_does_not(pop_db, tmp_path):
    """A NULL tranche is its own population: the group still forms under R1, fails R2, and is NOT a
    same-population duplicate under R3."""
    with pop_db.begin() as c:
        _seed(c, untagged_partner=True)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 2
    assert state["readings"]["R1"] == SMALL_R1
    assert state["readings"]["R2"] == {"meeting": SMALL_R1 - 1, "of": SMALL_R1}
    assert _met(state)["R2"] is False and _met(state)["R3"] is True
    assert state["diagnostics"]["untagged_complete_run1_rows"] == 1


@pytest.mark.postgres
def test_R4_fails_when_an_exception_has_no_census_row(pop_db, tmp_path):
    with pop_db.begin() as c:
        _seed(c, drop_fat2_census=True)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 2
    assert state["readings"]["R4"] == 2
    assert _met(state) == {"R1": True, "R2": True, "R3": True, "R4": False}
    assert state["diagnostics"]["R4_detail"]["Q9NYQ8"]["census_whole_complete"] == 0


@pytest.mark.postgres
def test_a_tile_with_no_run_label_is_counted_outside_the_key_and_moves_no_reading(pop_db, tmp_path):
    """⚠ The run-label predicate, measured: an unlabelled tile is invisible to every R-reading and
    appears only in the '(absent)' diagnostic."""
    with pop_db.begin() as c:
        _seed(c, unlabelled_tile=True)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 0
    assert state["readings"]["R1"] == SMALL_R1 and state["readings"]["R4"] == 3
    assert state["diagnostics"]["complete_rows_by_run_label"]["(absent)"] == 1
    assert state["diagnostics"]["R4_detail"]["Q8WXI7"]["census_tile_complete"] == 2, \
        "the unlabelled tile is outside the key, so R4's tile diagnostic does not see it"


@pytest.mark.postgres
def test_the_tranche0_run_label_diagnostic_reports_the_cohort_side(pop_db, tmp_path):
    with pop_db.begin() as c:
        _seed(c)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 0
    assert state["diagnostics"]["tranche0_complete_rows_by_run_label"] == {"1": SMALL_R1}


@pytest.mark.postgres
def test_an_empty_population_fails(pop_db, tmp_path):
    with pop_db.begin() as c:
        _seed(c, empty=True)
    rc, state, _, _ = _run(pop_db, tmp_path)
    assert rc == 2
    assert _met(state)["R1"] is False and _met(state)["R4"] is False


@pytest.mark.postgres
def test_a_list_capped_below_the_count_moves_no_reading(pop_db, tmp_path, capsys, monkeypatch):
    """⚠⚠ The LIMIT 50 defect, reproduced and refused: cap the list at 1 over 2 groups."""
    r = _module()
    monkeypatch.setattr(r, "LIST_CAP", 1)
    with pop_db.begin() as c:
        _seed(c)
    rc, state, _, printed = _run(pop_db, tmp_path, capsys)
    assert rc == 0
    assert state["readings"]["R1"] == SMALL_R1
    g = state["diagnostics"]["R1_groups"]
    assert g["count"] == SMALL_R1 and g["rows_shown"] == 1 and g["capped"] is True
    assert "CAPPED" in printed


@pytest.mark.postgres
def test_the_read_executes_no_mutation_and_opens_read_only(pop_db, tmp_path):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    with pop_db.begin() as c:
        _seed(c)
    seen: list[str] = []

    def spy(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(Engine, "before_cursor_execute", spy)
    try:
        rc, _, _, _ = _run(pop_db, tmp_path)
    finally:
        event.remove(Engine, "before_cursor_execute", spy)
    assert rc == 0
    assert any(s.strip() == "SET TRANSACTION READ ONLY" for s in seen)
    assert not [s for s in seen if _MUTATING.search(s)]


@pytest.mark.postgres
def test_the_evidence_file_is_never_overwritten(pop_db, tmp_path):
    with pop_db.begin() as c:
        _seed(c)
    _run(pop_db, tmp_path)
    r = _module()
    with pytest.raises(SystemExit):
        r.main(["--url", pop_db.url.render_as_string(hide_password=False),
                "--out", str(tmp_path / "r1r4_read.json")])


from test_d166_collapse_guards import pre_0014  # noqa: E402,F401  (fixture)
