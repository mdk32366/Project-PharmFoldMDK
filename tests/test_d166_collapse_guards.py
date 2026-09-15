"""F-079 — the collapse refuses the wrong cluster, a live fold, and a row something else references.

⚠⚠ **WHY THIS FILE EXISTS.** `scripts/d166_collapse_duplicate_tiles.py` is the one irreversible
production `DELETE` in the tree. At `d33027b` it never asked the database which database it was
(`D-159`), took its target from a hard-coded port, and carried *"must not run during a live fold"* as
prose. The forensic cluster holds the same three duplicates, so nothing about the data would have
refused it.

⚠ **How these are made to fail on the old script, not only pass on the new one.** Every run goes
through `_run`, which sets `sys.argv` and calls `main()` with no arguments — the calling shape both
versions accept. A crash is returned as the exception object, never as a refusal: **every assertion
names the exact return code**, so a script that dies on a missing `.env` fails `rc == 1` rather than
passing it by accident (`F-045`: a proof that cannot fail is not a proof).

⚠ Tests 3–5 are `@pytest.mark.postgres` (the `postgres` CI job, against the migrated chain). The
live marker is created by the fixture and DROPPED after it — `test_no_migration_creates_the_live_
marker` forbids the chain from placing it, and a marker left behind would make every later identity
refusal in the same database pass.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "d166_collapse_duplicate_tiles.py"


def _run(argv, monkeypatch):
    import scripts.d166_collapse_duplicate_tiles as c

    monkeypatch.setattr(sys, "argv", ["d166_collapse_duplicate_tiles.py", *argv])
    monkeypatch.setattr(c, "_fetch", lambda analysis_id: (1234, "ab" * 32))
    try:
        return c.main()
    except SystemExit as e:
        return e.code
    except Exception as e:  # noqa: BLE001 - a crash is recorded, never read as a refusal
        return e


# ── static: where the target comes from, and what is asked first ────────────────────────────────

def test_collapse_takes_its_url_from_the_operator_not_from_env_file():
    """⚠ `D-162` rule 5: a port number is not a cluster identity. The operator names the target
    (`--url`, or `DATABASE_URL`), the `f078_null_tier_the_37.py` shape."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"--url"' in src, "the collapse does not accept --url"
    assert "DATABASE_URL" in src
    assert not re.search(r"^PORT\s*=", src, re.M), "a hard-coded port is still the target"
    # ⚠ A PATH literal, not the substring: the first version asserted `".env" not in src` and
    # failed on `os.environ` — a crude assertion failing for the wrong reason. The old script's
    # read was `(REPO / ".env")`, which this still catches.
    assert not re.search(r"""["'/\\]\.env["'\s)]""", src), "the collapse still reads a dotenv file"


def test_collapse_identity_check_precedes_the_first_read_that_decides():
    """⚠ Order is the substance. The duplicate set decides what is deleted, so the database must
    have said which database it is before that read is taken."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "from core.db_identity import" in src
    assert "assert_campaign_target(" in src, "the collapse never calls the identity check"
    call = src.index("assert_campaign_target(")
    first_read = src.index("execute(DUPLICATES_SQL")
    assert call < first_read, "the duplicate set is read before the identity check"


# ── postgres: the three refusals, each with its negative control ────────────────────────────────

EXPECTED_PAIRS = {("2817", 0): (3673, 3693), ("2837", 1): (3674, 3695), ("2917", 0): (3675, 3696)}


def _seed_population(conn, n):
    from core.db_identity import ANCHOR_ACCESSION

    conn.execute(text(
        "INSERT INTO protein_analyses (input_type, input_value, cohort_tranche, metadata) "
        "VALUES ('uniprot', :v, 1, '{}')"),
        [{"v": ANCHOR_ACCESSION}] + [{"v": f"P{i:05d}"} for i in range(n - 1)])


def _seed_duplicates(conn):
    """The three `F-077` pairs at their real job ids, each job with its own analysis row."""
    for (parent, tile), ids in EXPECTED_PAIRS.items():
        for job_id in ids:
            aid = conn.execute(text(
                "INSERT INTO protein_analyses (input_type, input_value, metadata, pdb_path) "
                "VALUES ('uniprot', 'Q-TILE', '{}', :p) RETURNING id"),
                {"p": f"/data/artifacts/{job_id}/structure.pdb"}).scalar_one()
            conn.execute(text(
                "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
                "VALUES (:j, :a, 'complete', 1, CAST(:s AS jsonb))"),
                {"j": job_id, "a": aid,
                 "s": f'{{"parent_job_id": {parent}, "tile_index": {tile}}}'})


def _counts(engine):
    with engine.connect() as c:
        return (c.execute(text("SELECT count(*) FROM jobs")).scalar(),
                c.execute(text("SELECT count(*) FROM protein_analyses")).scalar())


#: ⚠ `0014`'s index, verbatim in effect. CI applies the whole chain, so the index exists there and
#: would refuse the very duplicates these tests must seed. Production is the other state — `0014` is
#: NOT applied, which is why the collapse exists — so the fixture reproduces production by dropping
#: it, and puts it back once the seeded rows are gone.
_TILE_INDEX = "uq_jobs_hold48_tile_identity"
_CREATE_TILE_INDEX = (
    f"CREATE UNIQUE INDEX {_TILE_INDEX} ON jobs "
    "((inference_settings->>'parent_job_id'), (inference_settings->>'tile_index')) "
    "WHERE inference_settings ? 'tile_index' AND inference_settings ? 'parent_job_id'")


@pytest.fixture
def pre_0014(pg_engine):
    """The migrated database as production holds it: `0014` not built, duplicates admissible."""
    from core.db_identity import LIVE_MARKER_TABLE

    with pg_engine.begin() as c:
        had_index = c.execute(text("SELECT to_regclass(:i)"), {"i": _TILE_INDEX}).scalar()
        c.execute(text(f"DROP INDEX IF EXISTS {_TILE_INDEX}"))
    try:
        yield pg_engine
    finally:
        with pg_engine.begin() as c:
            c.execute(text(f"DROP TABLE IF EXISTS {LIVE_MARKER_TABLE}"))
            c.execute(text(
                "TRUNCATE TABLE jobs, protein_analyses, ranking_runs RESTART IDENTITY CASCADE"))
            if had_index is not None:
                c.execute(text(_CREATE_TILE_INDEX))


@pytest.fixture
def live_db(pre_0014):
    """A migrated database that passes `D-159`: marker, floor, anchor, and the three duplicates."""
    from core.db_identity import CENSUS_FLOOR, LIVE_CLUSTER_ID, LIVE_MARKER_TABLE

    with pre_0014.begin() as c:
        c.execute(text(f"CREATE TABLE {LIVE_MARKER_TABLE} (cluster_id text NOT NULL)"))
        c.execute(text(f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c)"),
                  {"c": LIVE_CLUSTER_ID})
        _seed_population(c, CENSUS_FLOOR)
        _seed_duplicates(c)
    return pre_0014


@pytest.mark.postgres
def test_collapse_refuses_without_the_live_marker(pre_0014, monkeypatch, capsys):
    """⚠⚠ The forensic cluster's shape: full population, the three duplicates, NO marker."""
    from core.db_identity import CENSUS_FLOOR, LIVE_MARKER_TABLE

    pg_engine = pre_0014
    with pg_engine.begin() as c:
        _seed_population(c, CENSUS_FLOOR)
        _seed_duplicates(c)
    url = pg_engine.url.render_as_string(hide_password=False)
    before = _counts(pg_engine)

    rc = _run(["--url", url, "--i-am-the-owner"], monkeypatch)

    assert rc == 1, f"no marker, and the collapse returned {rc!r} instead of refusing"
    assert _counts(pg_engine) == before, "rows were deleted from an unmarked database"
    assert LIVE_MARKER_TABLE in capsys.readouterr().out


@pytest.mark.postgres
def test_collapse_dry_run_proceeds_on_the_marked_database(live_db, monkeypatch):
    """Negative control for the refusal above: marker present, same data, the dry run returns 0
    and writes nothing."""
    url = live_db.url.render_as_string(hide_password=False)
    before = _counts(live_db)
    rc = _run(["--url", url], monkeypatch)
    assert rc == 0, f"the dry run on a correct database returned {rc!r}"
    assert _counts(live_db) == before


@pytest.mark.postgres
def test_collapse_refuses_during_a_live_fold(live_db, monkeypatch, capsys):
    """⚠ `D-162` rule 3: *"must not run during a live fold"* was prose. A `claimed` job refuses,
    and the refusal names it."""
    url = live_db.url.render_as_string(hide_password=False)
    with live_db.begin() as c:
        aid = c.execute(text(
            "INSERT INTO protein_analyses (input_type, input_value, metadata) "
            "VALUES ('uniprot', 'P-LIVE', '{}') RETURNING id")).scalar_one()
        c.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (9001, :a, 'claimed', 1, '{}')"), {"a": aid})
    before = _counts(live_db)

    rc = _run(["--url", url, "--i-am-the-owner"], monkeypatch)

    assert rc == 1, f"a job is claimed and the collapse returned {rc!r}"
    assert _counts(live_db) == before
    assert "9001" in capsys.readouterr().out, "the refusal does not name the claimed job"


@pytest.mark.postgres
def test_collapse_refuses_when_a_job_names_a_dropped_row_as_its_json_parent(live_db, monkeypatch,
                                                                            capsys):
    """⚠ `ORDERS` A2.1. The catalog sees DECLARED foreign keys only. `inference_settings->>
    'parent_job_id'` points at `jobs.id` from inside JSON and no constraint declares it, so a
    `pg_constraint` enumeration is blind to it by construction. It is checked by name, as a
    non-constraint reference. Negative control: `test_collapse_dry_run_proceeds_on_the_marked_
    database`, where no job names a drop row."""
    url = live_db.url.render_as_string(hide_password=False)
    with live_db.begin() as c:
        aid = c.execute(text(
            "INSERT INTO protein_analyses (input_type, input_value, metadata) "
            "VALUES ('uniprot', 'P-CHILD', '{}') RETURNING id")).scalar_one()
        c.execute(text(
            "INSERT INTO jobs (id, analysis_id, status, attempts, inference_settings) "
            "VALUES (9002, :a, 'complete', 1, CAST('{\"parent_job_id\": 3693, \"tile_index\": 5}' "
            "AS jsonb))"), {"a": aid})
    before = _counts(live_db)

    rc = _run(["--url", url], monkeypatch)

    out = capsys.readouterr().out
    assert rc == 1, f"a job names a dropped row as its parent and the dry run returned {rc!r}"
    assert _counts(live_db) == before
    assert "9002" in out and "parent_job_id" in out, "the refusal does not name the JSON reference"


@pytest.mark.postgres
def test_collapse_refuses_when_another_table_references_a_dropped_row(live_db, monkeypatch, capsys):
    """⚠ A delete that fails on a foreign key mid-transaction is safe; one that cascades is not, and
    the dry run is the only place to find out before the owner's run. The references are
    enumerated from the CATALOG, so a table added by a later migration is seen without editing a
    list. Negative control: the same database without the reference is covered by
    `test_collapse_dry_run_proceeds_on_the_marked_database`."""
    url = live_db.url.render_as_string(hide_password=False)
    with live_db.begin() as c:
        drop_aid = c.execute(text("SELECT analysis_id FROM jobs WHERE id = 3693")).scalar_one()
        c.execute(text(
            "INSERT INTO protein_features (analysis_id, null_reasons) "
            "VALUES (:a, CAST('{}' AS jsonb))"), {"a": drop_aid})
    before = _counts(live_db)

    rc = _run(["--url", url], monkeypatch)

    out = capsys.readouterr().out
    assert rc == 1, f"a dropped analysis is referenced and the dry run returned {rc!r}"
    assert _counts(live_db) == before
    assert "protein_features" in out and "analysis_id" in out, (
        "the refusal does not name the referencing table and column")
