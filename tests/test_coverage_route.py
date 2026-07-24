"""D-038 coverage-route tests, written against the ruling BEFORE the code.

`GET /api/coverage` is the supplier UI Plan v2 §3.3/§4.1 need and the read API cannot be:
the manifest is the source of the **82** (deterministic, committed), the DB is the join for
**fold_status** only. Hermetic: the real `core/manifest.py` over the committed cohort CSV (so
the denominator is genuinely 82) + an in-memory SQLite seeded with a couple of folded rows.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base, JobRecord, ProteinAnalysis

TOKEN = "test-secret-token"

# Two named exclusions (D-022) and one cohort target we mark folded, all from the real cohort.
MUC16 = "Q8WXI7"
FAT2 = "Q9NYQ8"
NECTIN4 = "Q96NY8"


class _DummyQueue:
    def claim(self, worker_id):  # pragma: no cover - reads never touch the queue
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _seed_folded(engine, accession: str, pdb_path: str = "/data/artifacts/1/structure.pdb") -> int:
    with Session(engine) as s:
        row = ProteinAnalysis(input_type="uniprot", input_value=accession,
                              structure_source="esmfold", mean_plddt=77.26, pdb_path=pdb_path,
                              meta={"gene": "NECTIN4"})
        s.add(row)
        s.flush()
        rid = row.id
        s.commit()
    return rid


def _seed_job(engine, accession: str, status: str, error: str | None = None,
              pdb_path: str | None = None) -> int:
    """A `protein_analyses` shell row (D-043: `pdb_path` NULL unless folded) plus a `jobs`
    row in `status`. Mirrors production, where `core.enqueue` writes the shell row first and
    the FK-bound job points at it. Returns the analysis id."""
    with Session(engine) as s:
        pa = ProteinAnalysis(input_type="uniprot", input_value=accession,
                             structure_source="esmfold", pdb_path=pdb_path,
                             mean_plddt=(77.26 if pdb_path else None),
                             meta={"gene": "SEED"})
        s.add(pa)
        s.flush()
        aid = pa.id
        s.add(JobRecord(analysis_id=aid, status=status, error=error, inference_settings={}))
        s.commit()
    return aid


def _client(engine) -> TestClient:
    app = create_app(engine=engine, artifact_root="/tmp", auth_token=TOKEN, queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


def _get(engine):
    r = _client(engine).get("/api/coverage")               # no auth header — /api is open (D-034)
    assert r.status_code == 200
    return r.json()


# ── the coverage object: partition, denominator, breakouts (D-024) ────────────

def test_partition_sums_to_the_denominator(engine):
    cov = _get(engine)["coverage"]
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == cov["denominator"]


def test_denominator_is_pinned_at_82(engine):
    # A cohort-data edit that changes the count is then a deliberate, visible change (D-038).
    assert _get(engine)["coverage"]["denominator"] == 82


def test_breakouts_are_subsets_not_summed_into_the_partition(engine):
    cov = _get(engine)["coverage"]
    # unmeasured_tier ⊆ ranked, no_topology ⊆ held_out — cut ACROSS the partition (D-024)
    assert cov["unmeasured_tier"] <= cov["ranked"]
    assert cov["no_topology"] <= cov["held_out"]
    # and they are NOT added into the denominator
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == cov["denominator"]


# ── rows: excluded by NAME with a reason (D-022) ──────────────────────────────

def test_excluded_targets_appear_by_name_with_a_reason(engine):
    rows = {r["accession"]: r for r in _get(engine)["rows"]}
    for acc, name in ((MUC16, "MUC16"), (FAT2, "FAT2")):
        assert rows[acc]["excluded"] is True
        assert rows[acc]["disposition"] == "excluded"
        assert rows[acc]["exclusion_reason"] and name in rows[acc]["exclusion_reason"]


def test_rows_cover_all_82(engine):
    assert len(_get(engine)["rows"]) == 82


# ── fold_status: the DB join, both directions (D-038) ─────────────────────────

def test_fold_status_reflects_the_db_join(engine):
    analysis_id = _seed_folded(engine, NECTIN4)
    rows = {r["accession"]: r for r in _get(engine)["rows"]}

    # a seeded, completed row → folded, carrying the analysis_id the drill-down links to
    assert rows[NECTIN4]["fold_status"] == "folded"
    assert rows[NECTIN4]["analysis_id"] == analysis_id

    # an excluded target that was never enqueued → not_folded, no analysis_id
    assert rows[MUC16]["fold_status"] == "not_folded"
    assert rows[MUC16]["analysis_id"] is None


def test_fold_status_defaults_to_not_folded_with_an_empty_db(engine):
    rows = _get(engine)["rows"]
    assert all(r["fold_status"] == "not_folded" and r["analysis_id"] is None for r in rows)


# ── fold_status: the third state — attempted-and-failed ≠ never-attempted (D-043) ─

# Real cohort accessions for the two failure modes the rerun list names (closeout §8).
IGF2R = "P11717"     # O(L³) OOM — asked 230 GiB
ADAM17 = "P78536"    # interrupted mid-fold


def test_a_terminal_failed_job_reads_failed_with_its_reason(engine):
    reason = "CUDA OOM: tri_att_start asked 230.33 GiB on a 94.98 GiB card"
    _seed_job(engine, IGF2R, status="failed", error=reason)
    row = {r["accession"]: r for r in _get(engine)["rows"]}[IGF2R]
    # attempted-and-failed is its own state, and it carries the reason, not just a flag (D-024/D-043)
    assert row["fold_status"] == "failed"
    assert row["fail_reason"] == reason
    assert row["analysis_id"] is None          # a failed fold is not a folded one — no drill-down link


def test_an_in_flight_job_is_not_a_failure(engine):
    # claimed/pending are in-flight (D-030 status machine); only a terminal `failed` counts (D-043).
    _seed_job(engine, IGF2R, status="claimed")
    row = {r["accession"]: r for r in _get(engine)["rows"]}[IGF2R]
    assert row["fold_status"] == "not_folded"
    assert row["fail_reason"] is None


def test_a_folded_row_beats_an_earlier_failed_job(engine):
    # A target that failed once and later folded reads `folded` — the success is the truth (D-043).
    _seed_job(engine, ADAM17, status="failed", error="interrupted")
    _seed_job(engine, ADAM17, status="complete", pdb_path="/data/artifacts/9/structure.pdb")
    row = {r["accession"]: r for r in _get(engine)["rows"]}[ADAM17]
    assert row["fold_status"] == "folded"
    assert row["fail_reason"] is None
    assert row["analysis_id"] is not None


def test_fail_reason_is_null_for_non_failed_rows(engine):
    _seed_folded(engine, NECTIN4)
    rows = _get(engine)["rows"]
    assert all(r["fail_reason"] is None for r in rows if r["fold_status"] != "failed")


def test_payload_failed_count_matches_the_failed_rows(engine):
    _seed_job(engine, IGF2R, status="failed", error="OOM")
    _seed_job(engine, ADAM17, status="failed", error="interrupted")
    payload = _get(engine)
    failed_rows = [r for r in payload["rows"] if r["fold_status"] == "failed"]
    # a sibling of `coverage`, NOT summed into the partition (D-043) — the partition still holds
    assert payload["failed"] == len(failed_rows) == 2
    cov = payload["coverage"]
    assert cov["ranked"] + cov["held_out"] + cov["excluded"] == cov["denominator"]


# ── auth: /api/coverage is open, and the prefix property still holds ──────────

def test_coverage_route_is_unauthenticated(engine):
    # explicit: no Authorization header, still 200 (the structural property is in test_read_routes)
    assert _client(engine).get("/api/coverage").status_code == 200
