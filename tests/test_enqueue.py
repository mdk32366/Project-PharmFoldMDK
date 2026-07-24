"""D-026 enqueue tests, written against the ruling BEFORE the code.

Hermetic tests run on in-memory SQLite via SQLAlchemy (the D-005 test-DB pattern —
create_all, NOT the migration chain). One `postgres`-marked test exercises the
app-runtime write/commit path on REAL Postgres — the seam D-026's Hazard names as
never-run — and proves the rows committed by re-reading on a fresh connection (the
env.py-bug class: a green insert that silently rolled back). Not a mock.
"""

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from core.enqueue import FetchedSequence, enqueue_cohort
from core.manifest import build_manifest
from db.models import Base, JobRecord, ProteinAnalysis, RankingRun

ROWS = build_manifest()
MODEL_REVISION = "75a3841ee059df2bf4d56688166c8fb459ddd97a"


def _fake_fetch(accession: str) -> FetchedSequence:
    # Long enough to slice any ECD span in the cohort (max folded end < 1700).
    return FetchedSequence(sequence="A" * 2500, uniprot_release="2024_06")


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)   # D-005 test path; NOT the migration chain
    with Session(engine) as s:
        yield s


def _analysis(session, acc):
    return session.execute(
        select(ProteinAnalysis).where(ProteinAnalysis.input_value == acc)
    ).scalars().one_or_none()


def _job_for(session, acc):
    a = _analysis(session, acc)
    return session.execute(
        select(JobRecord).where(JobRecord.analysis_id == a.id)
    ).scalars().one()


def test_eighty_enqueued_two_excluded_get_no_job(session):
    s = enqueue_cohort(session, ROWS, _fake_fetch)
    assert (s.created, s.existed, s.excluded, s.enqueued) == (80, 0, 2, 80)
    assert session.scalar(select(func.count()).select_from(JobRecord)) == 80
    assert session.scalar(select(func.count()).select_from(ProteinAnalysis)) == 80
    for acc in ("Q8WXI7", "Q9NYQ8"):        # MUC16, FAT2 — no analysis, no job (D-022)
        assert _analysis(session, acc) is None


def test_re_run_is_idempotent(session):
    first = enqueue_cohort(session, ROWS, _fake_fetch)
    second = enqueue_cohort(session, ROWS, _fake_fetch)
    assert (first.created, first.existed) == (80, 0)
    assert (second.created, second.existed) == (0, 80)          # reports "exists"
    assert second.ranking_run_id == first.ranking_run_id        # same run, not a new one
    assert session.scalar(select(func.count()).select_from(JobRecord)) == 80          # no dupes
    assert session.scalar(select(func.count()).select_from(RankingRun)) == 1


def test_inference_settings_are_tier_correct(session):
    enqueue_cohort(session, ROWS, _fake_fetch)
    local = _job_for(session, "P55064")     # AQP5, largest span 18 <= 440 -> local
    assert (local.inference_settings["dtype"], local.inference_settings["chunk_size"]) == ("int8", 64)
    rental = _job_for(session, "P00533")    # EGFR, 621 in (440,630) -> rental
    # D-042: rental chunks like local now — the trunk's O(L^3) attention OOMs unchunked even on a
    # 95 GiB card (IGF2R asked 230 GiB), so chunk_size is 64, not None.
    assert (rental.inference_settings["dtype"], rental.inference_settings["chunk_size"]) == ("fp16", 64)
    revs = {j.inference_settings["model_revision"]
            for j in session.execute(select(JobRecord)).scalars()}
    assert revs == {MODEL_REVISION}          # pinned on every job (reproducibility)


def test_slice_provenance_and_uniprot_release_recorded(session):
    enqueue_cohort(session, ROWS, _fake_fetch)
    egfr = _analysis(session, "P00533").meta        # sliced_ecd, 25-645
    assert egfr["source"] == "sliced_ecd"
    assert (egfr["ecd_start"], egfr["ecd_end"], egfr["fold_length"]) == (25, 645, 621)
    assert egfr["uniprot_release"] == "2024_06"     # names WHICH UniProt (D-026 i)
    assert len(egfr["sequence"]) == 621             # the exact residues folded, stored
    sdk1 = _analysis(session, "Q7Z5N4").meta        # whole
    assert sdk1["source"] == "whole" and sdk1["ecd_start"] is None


def test_every_job_fks_a_real_analysis(session):
    enqueue_cohort(session, ROWS, _fake_fetch)
    analysis_ids = {a.id for a in session.execute(select(ProteinAnalysis)).scalars()}
    jobs = list(session.execute(select(JobRecord)).scalars())
    assert jobs and all(j.analysis_id in analysis_ids and j.status == "pending" for j in jobs)


# ── The app-runtime seam D-026 names as never-run: exercised on REAL Postgres ──
@pytest.mark.postgres
def test_enqueue_commits_on_real_postgres(pg_engine):
    """First application write on the app-runtime connection (D-026 Hazard). Prove
    the rows COMMITTED by re-reading on a fresh connection — the env.py-bug class
    where a green insert silently rolled back."""
    with Session(pg_engine) as s:
        summary = enqueue_cohort(s, ROWS, _fake_fetch)
    assert (summary.created, summary.excluded) == (80, 2)
    with pg_engine.connect() as c:      # fresh connection: did the writes stick?
        assert c.execute(select(func.count()).select_from(JobRecord)).scalar_one() == 80
        assert c.execute(select(func.count()).select_from(ProteinAnalysis)).scalar_one() == 80
        assert c.execute(select(func.count()).select_from(RankingRun)).scalar_one() == 1
