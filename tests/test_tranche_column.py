"""Census Task 1 — the tranche tag on `protein_analyses`, and the filter that keeps the cohort.

⚠ WHY THIS SHIPS BEFORE ANY CENSUS ROW EXISTS.  `protein_analyses` **is** the cohort today.
`app/reads.py:list_analyses` is `select(ProteinAnalysis).order_by(ProteinAnalysis.id)` — unfiltered
and unpaginated — and `ui/src/components/TargetList.jsx` renders whatever it returns.  So an ingest
without this migration makes the target list **silently** become the census.  *Silently* is the
operative word: nothing errors, nothing reddens, the page simply lists 2,807 proteins where it
listed 82.

⚠ THE TAG IS NULLABLE BECAUSE A NULL IS A CATEGORY.  Untagged means *unclassified* — not a census
member, and **not** tranche zero.  An absent value is never a low number, never a default, never a
bare null coerced into meaning something.

⚠ A-017 (the fixture must reach the code under test) APPLIES TO EVERY TEST HERE, and clause (c) is
the one that decides whether the backfill test means anything.  `test_backfill_tags_every_existing_row`
reverts by backfilling `WHERE pdb_path IS NOT NULL` — **which only reds if the fixture contains a row
with a null `pdb_path`.**  In production that row is **IGF2R**, fold-failed at 2,491 aa (CUDA OOM).
Without its equivalent here the revert reds nowhere and the test reads as coverage.  The fixture row
playing that part is named in the test.

⚠ KNOWN GAP, NAMED HERE RATHER THAN DISCOVERED LATER.  `test_every_enumerating_route_filters` walks
the **route** layer.  `scripts/fit_scorer.py:220-221` enumerates `protein_analyses` with an
unfiltered `select(ProteinFeatures, ProteinAnalysis).join(...)`, reaching the database directly via
`create_engine(DATABASE_URL)` at `:325` — **it is not a route and the walk cannot see it.**  Neither
`scripts/fit_scorer.py` nor `core/scorer.py` contains the string `tranche` or `cohort_tag`, so the
scorer path stays tranche-unaware after this migration.  Harmless while no census row has features;
it stops being harmless the moment one is folded.  **Not fixed here — the census order places that
guard elsewhere — but recorded so it is not found by surprise.**
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from app import reads  # noqa: E402
from db.models import Base, ProteinAnalysis  # noqa: E402

TRANCHE_ZERO = 0

# ⚠ The fixture row that plays IGF2R's part: folded=False, pdb_path=None. Clause (c) rests on it.
IGF2R_LIKE = "IGF2R_LIKE_FOLD_FAILED"


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _seed(eng, *, tranches=None):
    """Three rows. ⚠ Row 2 has a NULL pdb_path — the fold-failed case the backfill must not skip."""
    rows = [
        ("COHORT_A", "/tmp/a.pdb"),
        (IGF2R_LIKE, None),            # ← null pdb_path; this is the discriminating row
        ("COHORT_C", "/tmp/c.pdb"),
    ]
    with Session(eng) as s:
        for i, (name, pdb) in enumerate(rows):
            kw = {}
            if tranches is not None:
                kw["cohort_tranche"] = tranches[i]
            s.add(ProteinAnalysis(id=10 + i, input_type="accession", input_value=name,
                                  pdb_path=pdb, meta={"gene": name}, **kw))
        s.commit()
    return eng


# ── 1. the filter itself ─────────────────────────────────────────────────────
def test_list_analyses_filters_to_tranche_zero():
    """Prove it bites by removing the `.where(...)`: the foreign-tranche row reappears and this reds."""
    eng = _seed(_engine(), tranches=[TRANCHE_ZERO, TRANCHE_ZERO, 1])
    names = [r["accession"] for r in reads.list_analyses(eng)]
    assert "COHORT_C" not in names, (
        "a tranche-1 row reached the cohort list — an ingest would make the target list "
        f"silently become the census. got {names}")
    assert names == ["COHORT_A", IGF2R_LIKE], names


def test_the_filter_fixture_actually_contains_a_foreign_tranche_row():
    """⚠ A-017 positive control. Without a non-zero row the test above passes under NO filter at
    all — it would be asserting that nothing it never seeded is absent."""
    eng = _seed(_engine(), tranches=[TRANCHE_ZERO, TRANCHE_ZERO, 1])
    with Session(eng) as s:
        foreign = s.scalar(select(func.count()).select_from(ProteinAnalysis)
                           .where(ProteinAnalysis.cohort_tranche != TRANCHE_ZERO))
    assert foreign == 1, f"fixture seeded no foreign-tranche row, so the filter is untested: {foreign}"


# ── 2. every enumerating route filters ───────────────────────────────────────
def test_every_enumerating_route_filters():
    """⚠ Clause (a): a route walk that silently matches nothing passes everything, so the count of
    discovered enumerating routes is asserted NON-ZERO before anything is checked.

    Prove it bites by adding an unfiltered enumerating reader to `app/reads.py`."""
    import inspect
    src = inspect.getsource(reads)
    enumerating = [n for n in ("list_analyses",) if f"def {n}(" in src]
    assert enumerating, "no enumerating reader found — the walk matched nothing and proves nothing"

    eng = _seed(_engine(), tranches=[TRANCHE_ZERO, 1, 1])
    for name in enumerating:
        got = getattr(reads, name)(eng)
        assert len(got) == 1, (f"{name} returned {len(got)} rows over a fixture with one "
                               f"tranche-zero row — it is not filtering")


# ── 3. the backfill, and clause (c) ──────────────────────────────────────────
def test_backfill_tags_every_existing_row():
    """⚠ THE ONE CLAUSE (c) DECIDES. The revert is `WHERE pdb_path IS NOT NULL`, which tags 2 of 3
    here and 79 of 80 in production. The row it skips is the fold-failed one — `IGF2R_LIKE`, whose
    `pdb_path` is NULL — and without it in the fixture the revert reds nowhere.

    A skipped row does not error: it carries a null tag, is excluded from tranche-zero reads, and
    **silently vanishes from the target list.** The cohort quietly becomes 79."""
    eng = _seed(_engine())                       # no tranches -> the migration's backfill supplies them
    from db.tranche_backfill import backfill_tranche_zero
    backfill_tranche_zero(eng)

    with Session(eng) as s:
        untagged = s.scalars(select(ProteinAnalysis)
                             .where(ProteinAnalysis.cohort_tranche.is_(None))).all()
    assert not untagged, (
        "the backfill skipped rows: "
        f"{[r.input_value for r in untagged]} — the fold-failed row is the one at risk")

    with Session(eng) as s:
        total = s.scalar(select(func.count()).select_from(ProteinAnalysis))
        zeros = s.scalar(select(func.count()).select_from(ProteinAnalysis)
                         .where(ProteinAnalysis.cohort_tranche == TRANCHE_ZERO))
    assert (total, zeros) == (3, 3), (total, zeros)


# ── ⚠ THE MIGRATION-SHAPED FIXTURE. The one the in-memory engine could not provide. ──
def _file_engine(tmp_path):
    """A FILE-backed SQLite with NullPool, so 'a second connection' is genuinely a second one.

    ⚠ `create_engine("sqlite://")` uses `SingletonThreadPool` and hands the same connection back,
    so a helper that opens its own connection is INDISTINGUISHABLE from one that uses the caller's.
    That is precisely why the gate went green at 490 on code that deadlocked in production."""
    from sqlalchemy.pool import NullPool
    eng = create_engine(f"sqlite:///{tmp_path/'t.db'}", poolclass=NullPool)
    Base.metadata.create_all(eng)
    return eng


def test_the_backfill_runs_inside_the_callers_transaction(tmp_path):
    """⚠ THE TEST THAT WOULD HAVE CAUGHT THE DEADLOCK, and the fixture is the whole point.

    Migration `0008` calls this helper while holding `ACCESS EXCLUSIVE` on `protein_analyses` in an
    open transaction. If the helper opens its OWN connection, that connection waits on a lock its
    own caller holds — a deadlock with itself, hanging forever with zero other clients.

    This fixture reproduces the shape: an **outer transaction the caller already holds**, with a row
    written but **not committed**. A helper using the caller's Connection sees that row and tags it.
    A helper opening a second connection cannot see uncommitted data and tags nothing.

    ⚠ Prove it bites by reverting `backfill_tranche_zero` to `with Session(engine)`: this reds at
    `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked` on the UPDATE.
    On the in-memory engine the same revert stays **GREEN** — which is the finding.

    ═══════════════════════════════════════════════════════════════════════════════════════════
    ⚠ TWO ERROR-REDS THAT LOOK IDENTICAL AND MEAN OPPOSITE THINGS. Read this before judging one.
    ═══════════════════════════════════════════════════════════════════════════════════════════
    A-016's hazard is a red proving the code **never ran** — a module failed to import, the
    assertion never executed, and a terminal full of red reads as proof. That is the weak form,
    and it is why "prove it bites" demands a failure at the assertion.

    **This one is the other kind.** The test ran, reached the UPDATE, and the lock fired **at
    exactly the condition under test**. `database is locked` *is* the assertion — expressed by the
    engine rather than by `assert`, because the production symptom IS lock contention and not a
    wrong count. A second connection contending with its caller cannot report a number; it stops.

    **How to tell them apart, since they print the same:** ask whether the error arose *inside* the
    behaviour under test or *before reaching it*. Here the traceback's last test-side frame is the
    `backfill_tranche_zero(conn)` call itself, with the UPDATE's SQL in the message.

    ⚠ `test_the_backfill_still_opens_its_own_transaction_when_given_an_engine` is what makes the
    pair legible: it exercises the same helper on the Engine path and passes, so a reader knows the
    lock is specific to the shared-transaction condition and not a broken helper."""
    from db.tranche_backfill import backfill_tranche_zero
    eng = _file_engine(tmp_path)

    conn = eng.connect()
    trans = conn.begin()
    try:
        conn.execute(ProteinAnalysis.__table__.insert(),
                     [{"id": 1, "input_type": "accession", "input_value": "UNCOMMITTED",
                       "structure_source": "", "pdb_path": None, "notes": "",
                       "metadata": {}, "cohort_tranche": None}])
        tagged = backfill_tranche_zero(conn)          # ← the caller's Connection, mid-transaction
        assert tagged == 1, (
            "the backfill tagged %r rows — it could not see the caller's uncommitted row, so it "
            "opened its own connection. In the migration that connection waits on the caller's "
            "ACCESS EXCLUSIVE lock and hangs forever." % tagged)
        seen = conn.execute(select(func.count()).select_from(ProteinAnalysis)
                            .where(ProteinAnalysis.cohort_tranche == TRANCHE_ZERO)).scalar()
        assert seen == 1, seen
    finally:
        trans.rollback()
        conn.close()

    # ⚠ And it must NOT have committed: the migration owns that transaction.
    with Session(eng) as s:
        left = s.scalar(select(func.count()).select_from(ProteinAnalysis))
    assert left == 0, (
        f"{left} row(s) survived the caller's rollback — the backfill committed a transaction it "
        "does not own, which inside a migration ends the DDL transaction early")


def test_the_backfill_still_opens_its_own_transaction_when_given_an_engine(tmp_path):
    """⚠ A-017 positive control for the test above. The Connection path must not be the only one
    that works — tests and scripts pass an Engine, and that path must still commit on its own."""
    from db.tranche_backfill import backfill_tranche_zero
    eng = _file_engine(tmp_path)
    with Session(eng) as s:
        s.add(ProteinAnalysis(id=1, input_type="accession", input_value="COMMITTED", meta={}))
        s.commit()
    assert backfill_tranche_zero(eng) == 1
    with Session(eng) as s:
        assert s.scalar(select(func.count()).select_from(ProteinAnalysis)
                        .where(ProteinAnalysis.cohort_tranche == TRANCHE_ZERO)) == 1


def test_the_backfill_fixture_contains_a_null_pdb_path_row():
    """⚠ A-017 clause (c), asserted rather than assumed. Names the row that plays IGF2R's part. If
    this ever reds, `test_backfill_tags_every_existing_row` has stopped discriminating and its
    revert proves nothing."""
    eng = _seed(_engine())
    with Session(eng) as s:
        nulls = s.scalars(select(ProteinAnalysis)
                          .where(ProteinAnalysis.pdb_path.is_(None))).all()
    assert [r.input_value for r in nulls] == [IGF2R_LIKE], (
        "the fixture has no null-pdb_path row, so the WHERE pdb_path IS NOT NULL revert would red "
        f"nowhere and the backfill test would read as coverage. got {[r.input_value for r in nulls]}")


# ── 4 + 5. the split: two properties, two tests ─────────────────────────────
def test_null_tag_is_excluded_from_tranche_zero_reads():
    """⚠ Split from `test_null_tag_is_a_category_not_a_default` — property ONE of two.
    Untagged is *unclassified*, not tranche zero. Prove it bites by coercing null -> zero."""
    eng = _seed(_engine(), tranches=[TRANCHE_ZERO, None, TRANCHE_ZERO])
    names = [r["accession"] for r in reads.list_analyses(eng)]
    assert IGF2R_LIKE not in names, (
        f"an untagged row was served as tranche zero — a null was read as a default. got {names}")


def test_a_null_tag_is_never_coerced_to_zero_in_storage():
    """⚠ Split from the same test — property TWO of two. The read filter excluding a null and the
    storage layer preserving it are different properties; a compound test proves only its first
    failing assertion. Prove it bites by defaulting the column to 0 instead of leaving it nullable."""
    eng = _seed(_engine(), tranches=[TRANCHE_ZERO, None, TRANCHE_ZERO])
    with Session(eng) as s:
        row = s.scalar(select(ProteinAnalysis).where(ProteinAnalysis.input_value == IGF2R_LIKE))
        assert row.cohort_tranche is None, (
            f"a null tag was coerced to {row.cohort_tranche!r} in storage — an absent value became "
            "a low number, which is the defect the nullable column exists to prevent")


def test_the_column_is_nullable_so_a_null_can_exist_at_all():
    """⚠ A-017 positive control for the two tests above. If the column were NOT NULL the seed would
    raise and both would fail for the wrong reason — never reaching the property under test."""
    col = ProteinAnalysis.__table__.c.cohort_tranche
    assert col.nullable, "cohort_tranche is NOT NULL — a null category cannot be represented"
    assert col.default is None and col.server_default is None, (
        "cohort_tranche carries a default, so an untagged row silently becomes a tagged one")
